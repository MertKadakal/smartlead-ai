import os
import requests
import logging
from config import config

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Yapay zekâ servisine özel hata sınıfı."""
    pass


class AIService:
    def __init__(self):
        # Ortam değişkenlerini doğrudan veya config üzerinden güvenli al
        env_mode = os.environ.get("FLASK_ENV", "development")
        active_config = config.get(env_mode, config.get("default"))
        
        # Öncelik ortam değişkeninde olsun
        self.api_key = os.environ.get("GROQ_API_KEY") or getattr(active_config, "GROQ_API_KEY", "")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.config = active_config

    def _get_system_prompt(self) -> str:
        """Sistem talimatını (BUSINESS_CONTEXT) yapılandırmadan okur."""
        return getattr(self.config, "BUSINESS_CONTEXT", "Sen yardımsever bir asistansın.")

    def yanit_uret(self, mesaj: str, gecmis: list = None) -> str:
        """Kullanıcı mesajını ve geçmişi alıp yapay zekâ yanıtını döndürür."""
        if not self.api_key or not self.api_key.strip():
            logger.warning("GROQ_API_KEY tanımlı değil veya boş.")
            return f"[Demo Modu]: GROQ_API_KEY tanımlanmamış. Mesajınız: '{mesaj}'"

        if gecmis is None:
            gecmis = []

        # 1. GEÇMİŞİ SINIRLA: Son 6 mesaj (3 tur soru-cevap)
        gecmis = gecmis[-6:]

        # Mesaj listesi oluşturma
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        for item in gecmis:
            if isinstance(item, dict) and "role" in item and "content" in item:
                messages.append({"role": item["role"], "content": str(item["content"])})
        messages.append({"role": "user", "content": str(mesaj)})

        headers = {
            "Authorization": f"Bearer {self.api_key.strip()}",
            "Content-Type": "application/json",
        }

        # 2. Llama 3.1 8B için ideal payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 1024,
        }

        try:
            # timeout: (bağlantı kurma: 5s, veri alma: 40s)
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=(5, 40)
            )

            if response.status_code != 200:
                logger.error(f"Groq API Hatası: {response.status_code} - {response.text}")
                raise AIServiceError(
                    f"Groq API Hatası ({response.status_code}): {response.text}"
                )

            data = response.json()
            choice = data["choices"][0]
            ham_yanit = choice.get("message", {}).get("content") or ""
            finish_reason = choice.get("finish_reason")

            yanit = ham_yanit.strip()

            if not yanit:
                if finish_reason == "length":
                    return "Yanıt üretilirken uzunluk sınırına ulaşıldı. Lütfen sorunuzu daha spesifik iletebilir misiniz?"
                return "Üzgünüm, şu anda bir yanıt oluşturulamadı. Lütfen tekrar dener misiniz?"

            return yanit

        except requests.exceptions.Timeout as e:
            logger.error(f"Groq API zaman aşımı: {str(e)}")
            raise AIServiceError("Yapay zekâ servisi zaman aşımına uğradı, lütfen tekrar deneyin.") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Bağlantı hatası: {str(e)}")
            raise AIServiceError(f"Servis bağlantı hatası: {str(e)}") from e
        except (KeyError, IndexError) as e:
            logger.error(f"Yanıt formatı hatası: {str(e)}")
            raise AIServiceError("API yanıt formatı geçersiz.") from e


# Singleton servis örneği
ai_service = AIService()