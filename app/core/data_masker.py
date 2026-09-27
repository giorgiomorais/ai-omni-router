import re
from typing import Dict, Tuple

class DataMasker:
    """Anonimizador e mascarador de dados pessoais e comerciais sensíveis (LGPD Shield)."""

    CPF_PATTERN = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"
    CNPJ_PATTERN = r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    CREDIT_CARD_PATTERN = r"\b(?:\d{4}[ -]?){3}\d{4}\b"

    @classmethod
    def mask(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """Substitui dados confidenciais por tokens anônimos e guarda o mapa de reversão."""
        reverse_map: Dict[str, str] = {}
        masked_text = text

        # Anonimiza CPF
        cpfs = re.findall(cls.CPF_PATTERN, masked_text)
        for idx, cpf in enumerate(cpfs, 1):
            token = f"[CPF_OCULTO_{idx}]"
            reverse_map[token] = cpf
            masked_text = masked_text.replace(cpf, token)

        # Anonimiza CNPJ
        cnpjs = re.findall(cls.CNPJ_PATTERN, masked_text)
        for idx, cnpj in enumerate(cnpjs, 1):
            token = f"[CNPJ_OCULTO_{idx}]"
            reverse_map[token] = cnpj
            masked_text = masked_text.replace(cnpj, token)

        # Anonimiza E-mails
        emails = re.findall(cls.EMAIL_PATTERN, masked_text)
        for idx, email in enumerate(emails, 1):
            token = f"[EMAIL_OCULTO_{idx}]"
            reverse_map[token] = email
            masked_text = masked_text.replace(email, token)

        return masked_text, reverse_map

    @classmethod
    def unmask(cls, text: str, reverse_map: Dict[str, str]) -> str:
        """Restaura os dados originais após o retorno da resposta da IA."""
        unmasked = text
        for token, original in reverse_map.items():
            unmasked = unmasked.replace(token, original)
        return unmasked
