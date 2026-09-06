import os
import requests
from config import config
import re

# Aktif yapılandırmayı al
env_mode = os.environ.get("FLASK_ENV", "development")
active_config = config.get(env_mode, config["default"])


class AIServiceError(Exception):
    """Yapay zekâ servisine özel hata sınıfı."""

    pass


class AIService:

    def __init__(self):
        self.api_key = active_config.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "qwen/qwen3.6-27b"

    def _get_system_prompt(self) -> str:
        """Sistem talimatını (BUSINESS_CONTEXT) yapılandırmadan okur."""
        return active_config.BUSINESS_CONTEXT

    def yanit_uret(self, mesaj: str, gecmis: list = None) -> str:
        """Kullanıcı mesajını ve geçmişi alıp yapay zekâ yanıtını döndürür."""
        if not self.api_key or self.api_key.strip() == "":
            return f"[Demo Modu]: GROQ_API_KEY tanımlanmamış. Mesajınız: '{mesaj}'"

        if gecmis is None:
            gecmis = []

        # 1. GEÇMİŞİ SINIRLA: Token patlamasını önlemek için sadece son 6 mesajı (3 tur soru-cevap) al
        gecmis = gecmis[-6:]

        # Mesaj listesi oluşturma
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        for item in gecmis:
            messages.append(item)
        messages.append({"role": "user", "content": mesaj})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 2. TOKEN LİMİTİNİ YÜKSELT: Model düşünceyi bitirip asıl cevaba geçebilsin
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.6,
            "max_tokens": 1024,  # 300 yerine 1024
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
            choice = data["choices"][0]
            ham_yanit = choice["message"].get("content") or ""
            finish_reason = choice.get("finish_reason")

            # 3. DÜŞÜNCE ETİKETLERİNİ TEMİZLE
            # Önce kapanmış <think>...</think> bloklarını temizle
            temiz_yanit = re.sub(
                r"<think>.*?</think>", "", ham_yanit, flags=re.DOTALL
            ).strip()

            # Eğer kapanış etiketi yoksa ve sadece düşünce kaldıysa temizle
            if "<think>" in temiz_yanit:
                temiz_yanit = re.sub(
                    r"<think>.*", "", temiz_yanit, flags=re.DOTALL
                ).strip()

            # 4. EMNİYET KİLİDİ: Eğer regex sonrası metin boş kaldıysa
            if not temiz_yanit:
                if finish_reason == "length":
                    return "Yanıt üretilirken uzunluk sınırına ulaşıldı. Lütfen sorunuzu daha kısa veya spesifik sorabilir misiniz?"
                # Model boş döndüyse ham yanıttan etiketleri ayıklayıp son çare olarak döndür
                temiz_yanit = ham_yanit.replace("<think>", "").replace("</think>", "").strip()
                if not temiz_yanit:
                    return "Üzgünüm, şu anda yanıt oluşturamadım. Lütfen tekrar dener misiniz?"

            return temiz_yanit

        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"Servis bağlantı hatası: {str(e)}") from e
        except (KeyError, IndexError) as e:
            raise AIServiceError(f"API yanıt formatı geçersiz: {str(e)}") from e


# Singleton servis örneği
ai_service = AIService()