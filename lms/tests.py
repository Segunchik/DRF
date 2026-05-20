from django.test import TestCase
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Course, Lesson, Subscription



User = get_user_model()


class LessonCRUDTests(APITestCase):
    def setUp(self):
        """Подготовка тестовых данных и настройка аутентификации"""
        # User = get_user_model()
        # Создаём пользователей
        self.user1 = User.objects.create(email='user1@example.com')
        self.user1.set_password('testpass123')
        self.user1.save()
        self.user2 = User.objects.create(email='user2@example.com')
        self.user2.set_password('testpass123')
        self.user2.save()


        # Создаём курс
        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание курса'
        )


        # Создаём уроки
        self.lesson1 = Lesson.objects.create(
            title='Урок 1',
            description='Содержание урока 1',
            course=self.course,
            owner=self.user1
        )

        self.lesson2 = Lesson.objects.create(
            title='Урок 2',
            description='Содержание урока 2',
            course=self.course,
            owner=self.user1
        )


        # Инициализируем клиент
        self.client = APIClient()

    def test_create_lesson_authenticated(self):
        """Тест создания урока авторизованным пользователем"""
        self.client.force_authenticate(user=self.user1)

        data = {
            'title': 'Новый урок',
            'description': 'Содержание нового урока',
            'course': self.course.id
        }

        response = self.client.post('/lms/lesson/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)
        self.assertEqual(Lesson.objects.last().title, 'Новый урок')

    def test_create_lesson_unauthenticated(self):
        """Тест создания урока неавторизованным пользователем"""
        data = {
            'title': 'Урок без авторизации',
            'description': 'Содержание',
            'course': self.course.id
        }

        response = self.client.post('/lms/lesson/create/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_lesson(self):
        """Тест получения урока"""
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(f'/lms/lesson/{self.lesson1.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Урок 1')

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.user1)

        updated_data = {
            'title': 'Обновлённый урок 1',
            'descroption': 'Новое содержание',
            'course': self.course.id
        }

        response = self.client.put(f'/lms/lesson/update/{self.lesson1.id}/', updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, 'Обновлённый урок 1')

    def test_update_lesson_non_owner(self):
        """Тест обновления урока не владельцем"""
        self.client.force_authenticate(user=self.user2)  # user2 — не владелец

        updated_data = {
            'title': 'Попытка обновления',
            'description': 'Не должно сработать',
            'course': self.course.id
        }

        response = self.client.put(f'/lms/lesson/update/{self.lesson1.id}/', updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(f'/lms/lesson/delete/{self.lesson1.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson1.id).exists())


class SubscriptionTests(APITestCase):
    def setUp(self):
        """Подготовка тестовых данных для тестов подписок"""
        self.user1 = User.objects.create(
            email='sub_user1',
            password='testpass123'
        )
        self.user2 = User.objects.create(
            email='sub_user2',
            password='testpass123'
        )

        self.course1 = Course.objects.create(title='Курс 1', description='Описание 1')
        self.course2 = Course.objects.create(title='Курс 2', description='Описание 2')

        self.client = APIClient()

    def test_subscribe_and_unsubscribe(self):
        """Тест подписки и отписки от курса"""
        self.client.force_authenticate(user=self.user1)

        # Подписка на курс 1
        subscribe_data = {'course_id': self.course1.id}
        response = self.client.post('/lms/subscription/', subscribe_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.user1, course=self.course1).exists())

        # Отписка от курса 1
        response = self.client.post('/lms/subscription/', subscribe_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.user1, course=self.course1).exists())

    def test_multiple_subscriptions(self):
        """Тест множественных подписок"""
        self.client.force_authenticate(user=self.user1)

        # Подписываемся на оба курса
        self.client.post('/lms/subscription/', {'course_id': self.course1.id}, format='json')
        self.client.post('/lms/subscription/', {'course_id': self.course2.id}, format='json')


        # Проверяем, что обе подписки созданы
        self.assertEqual(Subscription.objects.filter(user=self.user1).count(), 2)

    def test_subscription_unauthenticated(self):
        """Тест попытки подписки неавторизованным пользователем"""
        response = self.client.post(
            '/lms/subscription/',
            {'course_id': self.course1.id},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        def test_course_list_with_subscription_status(self):
            """Тест списка курсов с признаком подписки"""
            self.client.force_authenticate(user=self.user1)

            # Подписываемся на курс 1
            self.client.post(
                '/lms/subscription/',
                {'course_id': self.course1.id},
                format='json'
            )

            # Получаем список курсов
            response = self.client.get('/lms/courses/', format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data['results'], list)

            # Проверяем статус подписки для каждого курса
            for course_data in response.data['results']:
                if course_data['id'] == self.course1.id:
                    self.assertTrue(course_data['is_subscribed'])
                else:
                    self.assertFalse(course_data['is_subscribed'])

        def test_subscription_to_nonexistent_course(self):
            """Тест подписки на несуществующий курс"""
            self.client.force_authenticate(user=self.user1)

            response = self.client.post(
                '/lms/subscription/',
                {'course_id': 9999},  # несуществующий ID
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        def test_invalid_course_id(self):
            """Тест передачи некорректного course_id"""
            self.client.force_authenticate(user=self.user1)

            response = self.client.post(
                '/lms/subscription/',
                {'course_id': 'invalid'},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        def test_duplicate_subscription(self):
            """Тест попытки создать дублирующую подписку"""
            self.client.force_authenticate(user=self.user1)

            # Создаём подписку
            self.client.post(
                '/lms/subscription/',
                {'course_id': self.course1.id},
                format='json'
            )

            # Пытаемся создать ту же подписку
            response = self.client.post(
                '/lms/subscription/',
                {'course_id': self.course1.id},
                format='json'
            )

            # Должна произойти отмена подписки (не ошибка)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Подписка удалена')

    class CourseListPaginationTests(APITestCase):
        def setUp(self):
            """Подготовка данных для тестирования пагинации"""
            self.user = User.objects.create_user(
                username='pag_user',
                password='testpass123'
            )

            # Создаём 15 курсов для тестирования пагинации (при page_size=10)
            for i in range(15):
                Course.objects.create(
                    title=f'Курс {i + 1}',
                    description=f'Описание курса {i + 1}'
                )

            self.client = APIClient()
            self.client.force_authenticate(user=self.user)

        def test_pagination_default_page_size(self):
            """Тест пагинации с размером страницы по умолчанию (10)"""
            response = self.client.get('/lms/courses/', format='json')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 10)  # 10 на странице
            self.assertEqual(response.data['pagination']['count'], 15)
            self.assertEqual(response.data['pagination']['total_pages'], 2)
            self.assertTrue(response.data['pagination']['has_next'])

        def test_pagination_custom_page_size(self):
            """Тест пагинации с кастомным размером страницы"""
            response = self.client.get(
                '/lms/courses/?page_size=5',
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data['results']), 5)
            self.assertEqual(response.data['pagination']['page_size'], 5)

        def test_pagination_max_page_size(self):
            """Тест ограничения максимального размера страницы"""
            response = self.client.get(
                '/lms/courses/?page_size=100',  # превышает max_page_size=50
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Должно быть не более 50 элементов
            self.assertLessEqual(len(response.data['results']), 50)
            self.assertEqual(response.data['pagination']['page_size'], 50)

        def test_pagination_page_navigation(self):
            """Тест навигации по страницам"""
            # Вторая страница
            response = self.client.get(
                '/lms/courses/?page=2&page_size=10',
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['pagination']['page'], 2)
            self.assertFalse(response.data['pagination']['has_next'])
