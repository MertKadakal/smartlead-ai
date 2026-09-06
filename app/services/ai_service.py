import os
import re
import requests
from config import config

env_mode = os.environ.get("FLASK_ENV", "development")
active_config = config.get(env_mode, config["default"])


class AIServiceError(Exception):
    """Yapay zekâ servisine özel hata sınıfı."""

    pass


class AIService:

    def __init__(self):
        # Render'daki Environment Variable'dan doğrudan okuma önceliği:
        self.api_key = os.environ.get("GROQ_API_KEY", "").strip() or getattr(
            active_config, "GROQ_API_KEY", ""
        )
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        # Groq üzerinde stabil çalışan güncel model:
        self.model = getattr(active_config, "GROQ_MODEL", "llama-3.3-70b-versatile")

    def _get_system_prompt(self) -> str:
        """Sistem talimatını (BUSINESS_CONTEXT) yapılandırmadan okur."""
        return getattr(
            active_config,
            "BUSINESS_CONTEXT",
            "Sen yardımcı bir yapay zeka asistanısın.",
        )

    def yanit_uret(self, mesaj: str, gecmis: list = None) -> str:
        """Kullanıcı mesajını ve geçmişi alıp yapay zekâ yanıtını döndürür."""
        # Anahtar sonradan eklendiyse kontrol et
        if not self.api_key:
            self.api_key = os.environ.get("GROQ_API_KEY", "").strip()

        if not self.api_key:
            return (
                "[Demo Modu]: GROQ_API_KEY tanımlanmamış. "
                f"Mesajınız alındı: '{mesaj}'"
            )

        if gecmis is None:
            gecmis = []

        messages = [{"role": "system", "content": self._get_system_prompt()}]

        for item in gecmis:
            if isinstance(item, dict) and "role" in item and "content" in item:
                messages.append(item)

        messages.append({"role": "user", "content": mesaj})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=30
            )

            if response.status_code != 200:
                raise AIServiceError(
                    f"Groq API Hatası ({response.status_code}): {response.text}"
                )

            data = response.json()
            ham_yanit = data["choices"][0]["message"]["content"]
            temiz_yanit = re.sub(
                r"<think>.*?</think>", "", ham_yanit, flags=re.DOTALL
            ).strip()
            return temiz_yanit

        except requests.exceptions.RequestException as e:
            raise AIServiceError(
                f"Servis bağlantı hatası oluştu: {str(e)}"
            ) from e
        except (KeyError, IndexError) as e:
            raise AIServiceError(
                f"API yanıtı beklenen formatta değil: {str(e)}"
            ) from e


ai_service = AIService()