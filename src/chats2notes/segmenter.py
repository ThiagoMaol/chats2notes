"""Módulo de segmentação determinística de transcripts em pares ordenados e arquivos de auditoria."""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SegmentTurn:
    """Representa um par de conversa (entrada do usuário + resposta visível da LLM)."""

    session_id: str
    user: str
    turn_index: int
    timestamp: str
    prompt: str
    response: str
    start_step: int
    end_step: int
    thinking: List[str] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


class TranscriptSegmenter:
    """Lê transcripts brutos do vault/raw/ e gera pares sequenciais e auditoria técnica."""

    def __init__(self, raw_dir: Path, segments_dir: Path):
        self.raw_dir = Path(raw_dir)
        self.segments_dir = Path(segments_dir)

    def parse_transcript(self, user: str, session_id: str, transcript_file: Path) -> List[SegmentTurn]:
        """Lê um arquivo JSONL e agrupa em turnos completos."""
        if not transcript_file.exists():
            return []

        turns: List[SegmentTurn] = []
        current_turn: Optional[SegmentTurn] = None
        turn_counter = 1

        with open(transcript_file, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                raw_line = line.strip()
                if not raw_line:
                    continue

                try:
                    step = json.loads(raw_line)
                except Exception as err:
                    logger.warning("Linha %d corrompida em %s: %s", line_idx, transcript_file, err)
                    continue

                if not isinstance(step, dict):
                    continue

                step_type = step.get("type", "")
                step_source = step.get("source", "")
                step_index = step.get("step_index", line_idx)

                # Identifica entrada do usuário
                is_user_input = step_type == "USER_INPUT" or step_source == "USER_EXPLICIT"

                if is_user_input:
                    # Se havia um turno anterior em andamento, verifica se possui resposta
                    if current_turn is not None and current_turn.response.strip():
                        turns.append(current_turn)
                        turn_counter += 1

                    current_turn = SegmentTurn(
                        session_id=session_id,
                        user=user,
                        turn_index=turn_counter,
                        timestamp=step.get("created_at", ""),
                        prompt=step.get("content", "").strip(),
                        response="",
                        start_step=step_index,
                        end_step=step_index,
                        thinking=[],
                        tool_calls=[],
                    )
                elif current_turn is not None:
                    # Passo de resposta / ferramentas do assistente
                    current_turn.end_step = step_index

                    # Coleta raciocínio interno (thinking)
                    thinking = step.get("thinking")
                    if thinking:
                        if isinstance(thinking, list):
                            for t in thinking:
                                if t and str(t).strip():
                                    current_turn.thinking.append(str(t).strip())
                        elif isinstance(thinking, str) and thinking.strip():
                            current_turn.thinking.append(thinking.strip())

                    # Coleta chamadas de ferramentas (tool_calls)
                    tool_calls = step.get("tool_calls")
                    if isinstance(tool_calls, list):
                        for tc in tool_calls:
                            if isinstance(tc, dict):
                                current_turn.tool_calls.append(tc)

                    # Coleta conteúdo de texto visível
                    content = step.get("content")
                    if content and isinstance(content, str) and content.strip():
                        if current_turn.response:
                            current_turn.response += "\n\n" + content.strip()
                        else:
                            current_turn.response = content.strip()

        # Ao final do arquivo, só inclui o último turno se houver resposta concluída
        if current_turn is not None and current_turn.response.strip():
            turns.append(current_turn)

        return turns

    def write_segment_markdown(self, turn: SegmentTurn, output_path: Path) -> None:
        """Grava o arquivo Markdown limpo 000X.md."""
        frontmatter = (
            f"---\n"
            f"session_id: {turn.session_id}\n"
            f"user: {turn.user}\n"
            f"turn: {turn.turn_index}\n"
            f'timestamp: "{turn.timestamp}"\n'
            f"start_step: {turn.start_step}\n"
            f"end_step: {turn.end_step}\n"
            f"---\n\n"
        )
        body = f"# Entrada\n\n{turn.prompt}\n\n# Resposta\n\n{turn.response}\n"
        output_path.write_text(frontmatter + body, encoding="utf-8")

    def write_segment_audit(self, turn: SegmentTurn, output_path: Path) -> None:
        """Grava o arquivo JSON paralelo 000X.audit.json para auditoria."""
        audit_payload = {
            "session_id": turn.session_id,
            "user": turn.user,
            "turn": turn.turn_index,
            "timestamp": turn.timestamp,
            "start_step": turn.start_step,
            "end_step": turn.end_step,
            "thinking": turn.thinking,
            "tool_calls": turn.tool_calls,
        }
        output_path.write_text(json.dumps(audit_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def segment_session(self, user: str, session_id: str, raw_session_dir: Path, output_session_dir: Path) -> int:
        """Regenera a pasta de segmentos de uma sessão a partir do raw."""
        transcript_file = raw_session_dir / "transcript_full.jsonl"
        turns = self.parse_transcript(user, session_id, transcript_file)

        # Regeneração atômica/limpa: cria ou limpa o diretório de destino
        output_session_dir.mkdir(parents=True, exist_ok=True)
        # Limpa arquivos antigos de segmentos para garantir sincronia com o raw
        for existing in output_session_dir.iterdir():
            if existing.is_file():
                existing.unlink()

        for turn in turns:
            prefix = f"{turn.turn_index:04d}"
            md_path = output_session_dir / f"{prefix}.md"
            self.write_segment_markdown(turn, md_path)

            if turn.thinking or turn.tool_calls:
                audit_path = output_session_dir / f"{prefix}.audit.json"
                self.write_segment_audit(turn, audit_path)

        return len(turns)

    def segment_all(self, target_session: Optional[str] = None) -> Dict[str, int]:
        """Varre o diretório vault/raw e segmenta todas as sessões ou a sessão especificada."""
        if not self.raw_dir.exists():
            return {"sessions_processed": 0, "turns_generated": 0}

        sessions_processed = 0
        turns_generated = 0

        for user_dir in sorted(self.raw_dir.iterdir()):
            if not user_dir.is_dir() or user_dir.name.startswith("."):
                continue

            for session_dir in sorted(user_dir.iterdir()):
                if not session_dir.is_dir() or session_dir.name.startswith("."):
                    continue

                session_id = session_dir.name
                if target_session and session_id != target_session:
                    continue

                output_session_dir = self.segments_dir / user_dir.name / session_id
                count = self.segment_session(
                    user=user_dir.name,
                    session_id=session_id,
                    raw_session_dir=session_dir,
                    output_session_dir=output_session_dir,
                )
                sessions_processed += 1
                turns_generated += count

        return {"sessions_processed": sessions_processed, "turns_generated": turns_generated}
