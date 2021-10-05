from django.test import TestCase
from django.test.client import Client
from django.utils.translation import activate
from home.models import Plan, App, Subscription
from decimal import Decimal
from django.contrib.auth import get_user_model


User = get_user_model()

class BaseTestCase(TestCase):
    def get_logged_client(self):
        client = Client()
        user_password = 'johnpassword'
        user = User.objects.create_user('john', 'lennon@thebeatles.com', user_password)
        response = client.post('/rest-auth/login/', {
            'username': user.username,
            'email': user.email,
            'password': user_password
        })
        return client, user

class PlanTest(BaseTestCase):
    def test_listing_plan(self):
        client, _ = self.get_logged_client()
        plan1 = Plan.objects.create(name='plan 1', description='desc plan 1', price=Decimal('1.11'))
        plan2 = Plan.objects.create(name='plan 2', description='desc plan 2', price=Decimal('2.22'))
        response = client.get('/api/v1/plans/')
        self.assertEquals(response.status_code, 200, 'I can list plans')
        self.assertEquals(len(response.data), 2, 'Two plans created')

        self.assertEquals(response.data[0]['id'], plan1.id, 'Plan 1 id correct')
        self.assertEquals(response.data[0]['name'], plan1.name, 'Plan 1 name correct')
        self.assertEquals(response.data[0]['description'], plan1.description, 'Plan 1 description correct')
        self.assertEquals(Decimal(response.data[0]['price']), plan1.price, 'Plan 1 price correct')

        self.assertEquals(response.data[1]['id'], plan2.id, 'Plan 2 id correct')
        self.assertEquals(response.data[1]['name'], plan2.name, 'Plan 2 name correct')
        self.assertEquals(response.data[1]['description'], plan2.description, 'Plan 2 description correct')
        self.assertEquals(Decimal(response.data[1]['price']), plan2.price, 'Plan 2 price correct')

    def test_reading_plan(self):
        plan1 = Plan.objects.create(name='plan 1', description='desc plan 1', price=Decimal('1.11'))
        client, _ = self.get_logged_client()
        response = client.get('/api/v1/plans/%s/' % plan1.id)
        self.assertEquals(response.status_code, 200, 'I can read a plan')
        self.assertEquals(response.data['name'], plan1.name, 'Plan 1 name correct')
        self.assertEquals(response.data['description'], plan1.description, 'Plan 1 description correct')
        self.assertEquals(Decimal(response.data['price']), plan1.price, 'Plan 1 price correct')

class SubsciptionTest(BaseTestCase):
    def test_creating_subscription(self):
        client, user = self.get_logged_client()
        plan = Plan.objects.create(name='plan1', description='plan 1 desc', price=Decimal('1.11'))
        app = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        response = client.post('/api/v1/subscriptions/',
                               {'active': True,
                                'plan': plan.id,
                                'app': app.id})
        self.assertEquals(response.status_code, 201, 'I can create a subscription')
        subscription = Subscription.objects.filter(id=response.data['id'])
        self.assertEquals(len(subscription), 1, 'Subscription created')
        subscription = subscription[0]
        self.assertEquals(subscription.active, True, 'Subscription active True')
        self.assertEquals(subscription.plan, plan, 'Subscription plan correct')
        self.assertEquals(subscription.app, app, 'Subscription app correct')

        # cached data
        self.assertEquals(subscription.user, subscription.app.user, 'User correct')
        self.assertEquals(subscription.app.subscription, subscription, 'Subscription correct')

    def test_listing_subscription(self):
        client, user = self.get_logged_client()
        plan = Plan.objects.create(name='plan1', description='plan 1 desc', price=Decimal('1.11'))
        app1 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        user2 = User.objects.create_user('john2', 'lennon2@thebeatles.com', 'johnpassword2')
        app2 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user2)
        subs1 = Subscription.objects.create(plan=plan, app=app1, active=True)
        subs2 = Subscription.objects.create(plan=plan, app=app2, active=True)
        response = client.get('/api/v1/subscriptions/')
        self.assertEquals(response.status_code, 200, 'I can list subscriptions')
        self.assertEquals(len(response.data), 1, 'I have one subscription')

        subscription = response.data[0]
        self.assertEquals(subscription['id'], subs1.id, 'Subscription id correct')
        self.assertEquals(subscription['active'], subs1.active, 'Subscription active True')
        self.assertEquals(subscription['plan'], subs1.plan.id, 'Subscription plan correct')
        self.assertEquals(subscription['app'], subs1.app.id, 'Subscription app correct')
        self.assertEquals(subscription['user'], user.id, 'Subscription user correct')

    def test_reading_subscription(self):
        client, user = self.get_logged_client()
        plan = Plan.objects.create(name='plan1', description='plan 1 desc', price=Decimal('1.10'))
        app1 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        subs1 = Subscription.objects.create(plan=plan, app=app1, active=True)
        response = client.get('/api/v1/subscriptions/%s/' % subs1.id)
        self.assertEquals(response.status_code, 200, 'I can read my subscription')
        subscription = response.data
        self.assertEquals(subscription['id'], subs1.id, 'Subscription id correct')
        self.assertEquals(subscription['active'], subs1.active, 'Subscription active True')
        self.assertEquals(subscription['plan'], subs1.plan.id, 'Subscription plan correct')
        self.assertEquals(subscription['app'], subs1.app.id, 'Subscription app correct')
        self.assertEquals(subscription['user'], user.id, 'Subscription user correct')

    def test_updating_subscription(self):
        client, user = self.get_logged_client()
        plan1 = Plan.objects.create(name='plan1', description='plan 1 desc', price=Decimal('1.11'))
        plan2 = Plan.objects.create(name='plan2', description='plan 2 desc', price=Decimal('2.22'))
        app1 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        app2 = App.objects.create(name='app 2', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        subs1 = Subscription.objects.create(plan=plan1, app=app1, active=True)
        response = client.put('/api/v1/subscriptions/%s/' % subs1.id, {
            'active': False,
            'plan': plan2.id,
            'app': app2.id
        }, content_type='application/json')
        self.assertEquals(response.status_code, 200, 'I can update my subscription')
        subscription = response.data
        self.assertEquals(subscription['id'], subs1.id, 'Subscription id correct')
        self.assertEquals(subscription['active'], False, 'Subscription active True')
        self.assertEquals(subscription['plan'], plan2.id, 'Subscription plan correct')
        self.assertEquals(subscription['app'], app2.id, 'Subscription app correct')
        self.assertEquals(subscription['user'], user.id, 'Subscription user correct')

    def test_partial_updating_subscription(self):
        client, user = self.get_logged_client()
        plan1 = Plan.objects.create(name='plan1', description='plan 1 desc', price=Decimal('1.11'))
        plan2 = Plan.objects.create(name='plan2', description='plan 2 desc', price=Decimal('2.22'))
        app1 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        app2 = App.objects.create(name='app 2', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        subs1 = Subscription.objects.create(plan=plan1, app=app1, active=True)
        response = client.patch('/api/v1/subscriptions/%s/' % subs1.id, {
            'active': False,
            'plan': plan2.id,
            'app': app2.id
        }, content_type='application/json')
        self.assertEquals(response.status_code, 200, 'I can update my subscription')
        subscription = response.data
        self.assertEquals(subscription['id'], subs1.id, 'Subscription id correct')
        self.assertEquals(subscription['active'], False, 'Subscription active True')
        self.assertEquals(subscription['plan'], plan2.id, 'Subscription plan correct')
        self.assertEquals(subscription['app'], app2.id, 'Subscription app correct')
        self.assertEquals(subscription['user'], user.id, 'Subscription user correct')

class AppTest(BaseTestCase):
    def test_creating_app(self):
        client, user = self.get_logged_client()
        app_name = 'app 1'
        response = client.post('/api/v1/apps/',
                               {'name': app_name,
                                'type': App.TYPE_WEB,
                                'framework': App.FRAMEWORK_DJANGO})
        self.assertEquals(response.status_code, 201, 'I can create an app')
        app = App.objects.filter(id=response.data['id'])
        self.assertEquals(len(app), 1, 'App created')
        app = app[0]
        self.assertEquals(app.name, app_name, 'App name correct')
        self.assertEquals(app.type, App.TYPE_WEB, 'App type correct')
        self.assertEquals(app.framework, App.FRAMEWORK_DJANGO, 'App framework correct')
        self.assertEquals(app.user, user, 'App user correct')

    def test_listing_app(self):
        client, user = self.get_logged_client()
        app1 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        user2 = User.objects.create_user('john2', 'lennon2@thebeatles.com', 'johnpassword2')
        app2 = App.objects.create(name='app2 2', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user2)
        response = client.get('/api/v1/apps/')
        self.assertEquals(response.status_code, 200, 'I can list apps')
        self.assertEquals(len(response.data), 1, 'I have one app')

        self.assertEquals(response.data[0]['id'], app1.id, 'App 1 id correct')
        self.assertEquals(response.data[0]['name'], app1.name, 'App 1 name correct')
        self.assertEquals(response.data[0]['type'], app1.type, 'App 1 type correct')
        self.assertEquals(response.data[0]['framework'], app1.framework, 'App 1 framework correct')
        self.assertEquals(response.data[0]['user'], user.id, 'App 1 user correct')

    def test_deleting_app(self):
        client, user = self.get_logged_client()
        app1 = App.objects.create(name='app 1', type=App.TYPE_WEB, framework=App.FRAMEWORK_DJANGO, user=user)
        response = client.delete('/api/v1/apps/%s/' % app1.id)
        self.assertEquals(response.status_code, 204, 'I can delete apps')
        self.assertEquals(App.objects.filter(pk=app1.id).count(), 0, 'I have no app')
