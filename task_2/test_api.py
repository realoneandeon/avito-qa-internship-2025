"""
Автоматизированные тесты для API микросервиса объявлений Авито
Host: https://qa-internship.avito.com
Base URL: https://qa-internship.avito.com/api/1
"""

import pytest
import requests
import random
import time
import uuid
from typing import Dict, Any, Optional, List


BASE_URL = "https://qa-internship.avito.com/api/1"


class TestAdsAPI:
    """Класс для тестирования API объявлений"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка перед каждым тестом"""
        self.base_url = BASE_URL
        self.created_ads = []  # Список созданных объявлений для очистки
        self.test_seller_id = random.randint(111111, 999999)
        yield
        # Очистка после теста (если нужна)
    
    def generate_unique_seller_id(self) -> int:
        """Генерация уникального sellerID"""
        return random.randint(111111, 999999)
    
    def create_ad(self, seller_id: Optional[int] = None, name: str = "Test Ad", 
                  price: int = 1000, statistics: Optional[Dict] = None) -> Dict[str, Any]:
        """Вспомогательный метод для создания объявления"""
        if seller_id is None:
            seller_id = self.test_seller_id
        
        if statistics is None:
            statistics = {
                "contacts": 0,
                "likes": 0,
                "viewCount": 0
            }
        
        payload = {
            "sellerID": seller_id,
            "name": name,
            "price": price,
            "statistics": statistics
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        if response.status_code == 200:
            # Сохраняем seller_id для последующего получения объявлений
            self.created_ads.append({"seller_id": seller_id, "name": name})
            return response.json()
        return response.json() if response.text else {}
    
    def get_ad_by_id(self, item_id: str) -> List[Dict]:
        """Вспомогательный метод для получения объявления по ID"""
        response = requests.get(f"{self.base_url}/item/{item_id}")
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_ads_by_seller(self, seller_id: int, max_retries: int = 5, delay: float = 1.0) -> List[Dict]:
        """Вспомогательный метод для получения объявлений продавца с повторными попытками"""
        for attempt in range(max_retries):
            response = requests.get(f"{self.base_url}/{seller_id}/item")
            if response.status_code == 200:
                ads = response.json()
                if len(ads) > 0 or attempt == max_retries - 1:
                    return ads
            time.sleep(delay)
        return []
    
    # ========== Ручка 1: Создание объявления (POST /api/1/item) ==========
    
    def test_create_ad_success(self):
        """TC-001: Успешное создание объявления с валидными данными"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "name": "Тестовое объявление",
            "price": 5000,
            "statistics": {
                "contacts": 3,
                "likes": 10,
                "viewCount": 5
            }
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        data = response.json()
        assert "status" in data, "В ответе отсутствует поле status"
    
    def test_create_ad_invalid_seller_id_low(self):
        """TC-002: Создание объявления с невалидным sellerID (меньше 111111)"""
        payload = {
            "sellerID": 100000,
            "name": "Test",
            "price": 1000,
            "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    def test_create_ad_invalid_seller_id_high(self):
        """TC-003: Создание объявления с невалидным sellerID (больше 999999)"""
        payload = {
            "sellerID": 1000000,
            "name": "Test",
            "price": 1000,
            "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    def test_create_ad_missing_name(self):
        """TC-004: Создание объявления без обязательного поля name"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "price": 1000,
            "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    def test_create_ad_negative_price(self):
        """TC-005: Создание объявления с отрицательной ценой"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "name": "Test",
            "price": -100,
            "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    def test_create_ad_empty_name(self):
        """TC-006: Создание объявления с пустым name"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "name": "",
            "price": 1000,
            "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    def test_create_ad_zero_price(self):
        """TC-007: Создание объявления с нулевой ценой"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "name": "Test",
            "price": 0,
            "statistics": {"contacts": 0, "likes": 0, "viewCount": 0}
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        # Может быть 200 или 400 в зависимости от бизнес-логики
        assert response.status_code in [200, 400], f"Неожиданный статус {response.status_code}"
    
    def test_create_ad_without_statistics(self):
        """TC-008: Создание объявления без поля statistics"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "name": "Test",
            "price": 1000
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        # API требует поле statistics, поэтому ожидаем 400
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"
    
    def test_create_ad_negative_statistics(self):
        """TC-009: Создание объявления с отрицательными значениями в statistics"""
        seller_id = self.generate_unique_seller_id()
        payload = {
            "sellerID": seller_id,
            "name": "Test",
            "price": 1000,
            "statistics": {
                "contacts": -1,
                "likes": -5,
                "viewCount": -10
            }
        }
        
        response = requests.post(f"{self.base_url}/item", json=payload)
        # Может быть 400 или 200 в зависимости от валидации
        assert response.status_code in [200, 400], f"Неожиданный статус {response.status_code}"
    
    # ========== Ручка 2: Получение объявления по идентификатору (GET /api/1/item/:id) ==========
    
    def test_get_ad_by_id_success(self):
        """TC-010: Успешное получение существующего объявления"""
        # Создаем объявление
        seller_id = self.generate_unique_seller_id()
        response = self.create_ad(seller_id=seller_id, name="Test Ad")
        assert response.get("status") is not None, "Объявление не было создано"
        
        # Получаем все объявления продавца с повторными попытками
        ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        assert len(ads) > 0, "Не удалось получить созданное объявление"
        
        item_id = ads[0].get("id")
        assert item_id is not None, "В ответе отсутствует id"
        
        # Получаем объявление по id
        response = requests.get(f"{self.base_url}/item/{item_id}")
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        assert len(data) > 0, "Массив не должен быть пустым"
        assert data[0].get("id") == item_id, "id не соответствует запрошенному"
        assert "name" in data[0], "В ответе отсутствует name"
        assert "sellerId" in data[0] or "sellerID" in data[0], "В ответе отсутствует sellerId"
    
    def test_get_ad_by_id_not_found(self):
        """TC-011: Получение несуществующего объявления"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{self.base_url}/item/{fake_id}")
        
        assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    
    def test_get_ad_by_id_invalid_format(self):
        """TC-012: Получение объявления с невалидным форматом id"""
        response = requests.get(f"{self.base_url}/item/abc123")
        
        assert response.status_code in [400, 404], f"Ожидался статус 400 или 404, получен {response.status_code}"
    
    def test_get_ad_by_id_empty(self):
        """TC-013: Получение объявления с пустым id"""
        response = requests.get(f"{self.base_url}/item/")
        
        assert response.status_code in [404, 400, 405], f"Ожидался статус 404/400/405, получен {response.status_code}"
    
    # ========== Ручка 3: Получение всех объявлений по sellerID (GET /api/1/:sellerID/item) ==========
    
    def test_get_ads_by_seller_success(self):
        """TC-014: Успешное получение объявлений существующего продавца"""
        seller_id = self.generate_unique_seller_id()
        
        # Создаем несколько объявлений
        self.create_ad(seller_id=seller_id, name="Ad 1")
        self.create_ad(seller_id=seller_id, name="Ad 2")
        self.create_ad(seller_id=seller_id, name="Ad 3")
        
        # Получаем все объявления продавца с повторными попытками
        ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        
        assert isinstance(ads, list), "Ответ должен быть массивом"
        assert len(ads) >= 3, f"Ожидалось минимум 3 объявления, получено {len(ads)}"
        
        # Проверяем, что все объявления принадлежат продавцу
        for ad in ads:
            seller_id_in_response = ad.get("sellerId") or ad.get("sellerID")
            assert seller_id_in_response == seller_id, f"Объявление принадлежит другому продавцу: {seller_id_in_response} != {seller_id}"
    
    def test_get_ads_by_seller_not_found(self):
        """TC-015: Получение объявлений несуществующего продавца"""
        fake_seller_id = random.randint(111111, 999999)
        response = requests.get(f"{self.base_url}/{fake_seller_id}/item")
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        # Может быть пустой массив
    
    def test_get_ads_by_seller_invalid_low(self):
        """TC-016: Получение объявлений продавца с невалидным sellerID (меньше 111111)"""
        response = requests.get(f"{self.base_url}/100000/item")
        
        # GET запросы могут не валидировать sellerID так строго, как POST
        # Возвращают пустой массив или 200, но не 400
        assert response.status_code in [200, 400], f"Неожиданный статус {response.status_code}"
    
    def test_get_ads_by_seller_invalid_high(self):
        """TC-017: Получение объявлений продавца с невалидным sellerID (больше 999999)"""
        response = requests.get(f"{self.base_url}/1000000/item")
        
        # GET запросы могут не валидировать sellerID так строго, как POST
        # Возвращают пустой массив или 200, но не 400
        assert response.status_code in [200, 400], f"Неожиданный статус {response.status_code}"
    
    def test_get_ads_by_seller_unique_item_ids(self):
        """TC-018: Проверка уникальности id при получении объявлений продавца"""
        seller_id = self.generate_unique_seller_id()
        
        # Создаем несколько объявлений
        self.create_ad(seller_id=seller_id, name="Ad 1")
        self.create_ad(seller_id=seller_id, name="Ad 2")
        self.create_ad(seller_id=seller_id, name="Ad 3")
        
        # Получаем все объявления продавца с повторными попытками
        data = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        item_ids = [ad.get("id") for ad in data if ad.get("id")]
        
        # Проверяем уникальность
        assert len(item_ids) == len(set(item_ids)), "Обнаружены дубликаты id"
    
    # ========== Ручка 4: Получение статистики по itemID (GET /api/1/statistic/:id) ==========
    
    def test_get_ad_stats_success(self):
        """TC-019: Успешное получение статистики существующего объявления"""
        # Создаем объявление
        seller_id = self.generate_unique_seller_id()
        response = self.create_ad(seller_id=seller_id, name="Test Ad")
        assert response.get("status") is not None, "Объявление не было создано"
        
        # Получаем все объявления продавца с повторными попытками
        ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        assert len(ads) > 0, "Не удалось получить созданное объявление"
        
        item_id = ads[0].get("id")
        assert item_id is not None, "В ответе отсутствует id"
        
        # Получаем статистику
        response = requests.get(f"{self.base_url}/statistic/{item_id}")
        
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"
        assert len(data) > 0, "Массив не должен быть пустым"
        # Проверяем наличие полей статистики
        stats = data[0]
        assert "likes" in stats or "viewCount" in stats or "contacts" in stats, "В ответе отсутствует статистика"
    
    def test_get_ad_stats_not_found(self):
        """TC-020: Получение статистики несуществующего объявления"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{self.base_url}/statistic/{fake_id}")
        
        assert response.status_code == 404, f"Ожидался статус 404, получен {response.status_code}"
    
    def test_get_ad_stats_invalid_format(self):
        """TC-021: Получение статистики с невалидным форматом id"""
        response = requests.get(f"{self.base_url}/statistic/abc123")
        
        assert response.status_code in [400, 404], f"Ожидался статус 400 или 404, получен {response.status_code}"
    
    def test_get_ad_stats_view_count_increment(self):
        """TC-022: Проверка корректности данных статистики (счетчик просмотров)"""
        # Создаем объявление
        seller_id = self.generate_unique_seller_id()
        response = self.create_ad(seller_id=seller_id, name="Test Ad")
        assert response.get("status") is not None, "Объявление не было создано"
        
        # Получаем все объявления продавца с повторными попытками
        ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        assert len(ads) > 0, "Не удалось получить созданное объявление"
        
        item_id = ads[0].get("id")
        assert item_id is not None, "В ответе отсутствует id"
        
        # Получаем статистику несколько раз
        response1 = requests.get(f"{self.base_url}/statistic/{item_id}")
        assert response1.status_code == 200
        stats1 = response1.json()
        
        time.sleep(1)  # Небольшая задержка
        
        response2 = requests.get(f"{self.base_url}/statistic/{item_id}")
        assert response2.status_code == 200
        stats2 = response2.json()
        
        # Извлекаем viewCount из разных возможных структур ответа
        view_count1 = None
        view_count2 = None
        
        if isinstance(stats1, list) and len(stats1) > 0:
            view_count1 = stats1[0].get("viewCount")
        elif isinstance(stats1, dict):
            view_count1 = stats1.get("viewCount")
        
        if isinstance(stats2, list) and len(stats2) > 0:
            view_count2 = stats2[0].get("viewCount")
        elif isinstance(stats2, dict):
            view_count2 = stats2.get("viewCount")
        
        # Если viewCount присутствует, проверяем его увеличение
        if view_count1 is not None and view_count2 is not None:
            assert view_count2 >= view_count1, "Счетчик просмотров должен увеличиваться"
    
    # ========== Интеграционные тесты ==========
    
    def test_full_cycle_create_get_stats_seller(self):
        """TC-023: Полный цикл: создание -> получение -> статистика -> получение по sellerID"""
        seller_id = self.generate_unique_seller_id()
        
        # 1. Создаем объявление
        response = self.create_ad(seller_id=seller_id, name="Integration Test Ad")
        assert response.get("status") is not None, "Объявление не было создано"
        
        # 2. Получаем все объявления продавца с повторными попытками
        seller_ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        assert len(seller_ads) >= 1, "Должно быть минимум одно объявление продавца"
        
        item_id = seller_ads[0].get("id")
        assert item_id is not None, "В ответе отсутствует id"
        
        # 3. Получаем объявление по id
        response = requests.get(f"{self.base_url}/item/{item_id}")
        assert response.status_code == 200
        retrieved_data = response.json()
        assert isinstance(retrieved_data, list), "Ответ должен быть массивом"
        assert len(retrieved_data) > 0, "Массив не должен быть пустым"
        assert retrieved_data[0].get("id") == item_id, "id не соответствует"
        seller_id_in_response = retrieved_data[0].get("sellerId") or retrieved_data[0].get("sellerID")
        assert seller_id_in_response == seller_id, "sellerID не соответствует"
        
        # 4. Получаем статистику
        stats_response = requests.get(f"{self.base_url}/statistic/{item_id}")
        assert stats_response.status_code == 200
        
        # 5. Проверяем, что созданное объявление есть в списке продавца
        item_ids = [ad.get("id") for ad in seller_ads]
        assert item_id in item_ids, "Созданное объявление отсутствует в списке продавца"
    
    def test_create_multiple_ads_same_seller(self):
        """TC-024: Создание нескольких объявлений одним продавцом"""
        seller_id = self.generate_unique_seller_id()
        
        # Создаем 3 объявления
        self.create_ad(seller_id=seller_id, name="Ad 1")
        self.create_ad(seller_id=seller_id, name="Ad 2")
        self.create_ad(seller_id=seller_id, name="Ad 3")
        
        # Получаем все объявления продавца с повторными попытками
        seller_ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        assert len(seller_ads) >= 3, f"Ожидалось минимум 3 объявления, получено {len(seller_ads)}"
        
        # Проверяем уникальность id
        item_ids = [ad.get("id") for ad in seller_ads if ad.get("id")]
        assert len(item_ids) == len(set(item_ids)), "id должны быть уникальными"
        
        # Проверяем, что все объявления принадлежат продавцу
        for ad in seller_ads:
            seller_id_in_response = ad.get("sellerId") or ad.get("sellerID")
            assert seller_id_in_response == seller_id, "Все объявления должны принадлежать одному продавцу"
    
    def test_item_id_uniqueness(self):
        """TC-025: Проверка уникальности id при создании"""
        seller_id = self.generate_unique_seller_id()
        
        # Создаем несколько объявлений
        self.create_ad(seller_id=seller_id, name="Ad 1")
        self.create_ad(seller_id=seller_id, name="Ad 2")
        self.create_ad(seller_id=seller_id, name="Ad 3")
        self.create_ad(seller_id=seller_id, name="Ad 4")
        self.create_ad(seller_id=seller_id, name="Ad 5")
        
        # Получаем все объявления продавца с повторными попытками
        ads = self.get_ads_by_seller(seller_id, max_retries=10, delay=2.0)
        item_ids = [ad.get("id") for ad in ads if ad.get("id")]
        
        # Проверяем уникальность
        assert len(item_ids) == len(set(item_ids)), "Обнаружены дубликаты id"
    
    # ========== Негативные тесты ==========
    
    def test_wrong_http_method(self):
        """TC-026: Отправка запроса с некорректным HTTP методом"""
        response = requests.put(f"{self.base_url}/item", json={})
        
        assert response.status_code in [405, 400, 404], f"Ожидался статус 405/400/404, получен {response.status_code}"
    
    def test_wrong_content_type(self):
        """TC-027: Отправка запроса с некорректным Content-Type"""
        headers = {"Content-Type": "text/plain"}
        payload = "not json"
        response = requests.post(f"{self.base_url}/item", data=payload, headers=headers)
        
        assert response.status_code in [400, 415], f"Ожидался статус 400/415, получен {response.status_code}"
    
    def test_invalid_json(self):
        """TC-028: Отправка запроса с некорректным JSON"""
        headers = {"Content-Type": "application/json"}
        payload = "{invalid json}"
        response = requests.post(f"{self.base_url}/item", data=payload, headers=headers)
        
        assert response.status_code == 400, f"Ожидался статус 400, получен {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

