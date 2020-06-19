import mock
from django.http import HttpResponseBadRequest
from django.test import TestCase
from django.urls import reverse

from base.models.enums.education_group_categories import Categories
from base.models.enums.education_group_types import GroupType
from education_group.forms.select_type import SelectTypeForm
from education_group.tests.factories.auth.central_manager import CentralManagerFactory


class TestSelectTypeCreateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.central_manager = CentralManagerFactory()
        cls.url = reverse('create_select_type', kwargs={'category': Categories.GROUP.name})

    def setUp(self) -> None:
        self.client.force_login(self.central_manager.person.user)

    def test_case_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_case_get_method_with_invalid_category_assert_bad_request(self):
        url_with_invalid_category = reverse('create_select_type', kwargs={'category': 'Unknown categ'})
        response = self.client.get(url_with_invalid_category)

        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)

    def test_case_get_assert_context(self):
        response = self.client.get(self.url)

        self.assertIsInstance(response.context['form'], SelectTypeForm)

    def test_case_post_method_with_invalid_category_assert_bad_request(self):
        url_with_invalid_category = reverse('create_select_type', kwargs={'category': 'Unknown categ'})
        response = self.client.post(url_with_invalid_category)

        self.assertEqual(response.status_code, HttpResponseBadRequest.status_code)

    @mock.patch('education_group.views.create.SelectTypeForm.is_valid', return_value=True)
    @mock.patch('education_group.views.create.SelectTypeForm.cleaned_data', new_callable=mock.PropertyMock, create=True)
    def test_case_group_type_valid_post_assert_redirect_to_group_create(self, mock_form_cleaned_data, *args, **kwargs):
        mock_form_cleaned_data.return_value = {'name': GroupType.COMMON_CORE.name}
        response = self.client.post(self.url, data={})

        self.assertRedirects(
            response,
            reverse('group_create', kwargs={'type': GroupType.COMMON_CORE.name})
        )

