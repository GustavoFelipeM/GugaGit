from dataclasses import asdict, dataclass
from typing import Optional, Any

@dataclass
class GitResult:
    sucesso: bool
    mensagem: str
    dados: Optional[Any] = None
    erro_detalhado: Optional[str] = None

    def to_dict(self):
        return asdict(self)