from django.urls import path
from myapp import views

urlpatterns = [
    #path('', views.index, name='index'),#对应<a href="{% url 'index' %}">Home</a>.
    path('', views.welcome, name='welcome'),
    path('index/', views.index,name='index'),
]


from . import views
urlpatterns += [
    path('make_request/', views.make_a_request, name='make-a-request'),
    #path('my_own_requests/',views.MyOwnRequestListView.as_view(),name='show-own-request'),
    path('my_own_requests/', views.MyOwnRequestListView.as_view(),name='show-own-request'),
    path('my_share_requests/', views.MyShareRequestListView.as_view(),name= 'show-share-request'),
    #path('my_drive_requests/',views.MyDriveRequestListView.as_view(),name='show-drive-request'),
    path('my_drive_requests/', views.drive_complete_request,name='show-drive-request'),
    path('open_requests/', views.RequestListDriverView.as_view(),name='all-requests'),
    path('registerAsUser/', views.registerAsUser, name='registerAsUser'),
    path('registerAsDriver/', views.registerAsDriver, name='registerAsDriver'),
    path('open_requests/<uuid:pk>', views.OrderConfirmView.order_confirm_view, name='order-detail'),
    path('requests/<uuid:pk>', views.RequestDetailView.request_detail_view,name='my-own-request-detail'),

]

urlpatterns +=[
    path('join_request/',views.make_a_share_request, name='make-a-share'),
    path('my_own_requests/edit_requests/<uuid:pk>', views.MyOwnRequestUpdateView.my_own_request_update_view, name='edit-my-own-request'),
    path('my_own_requests/delete_requests/<uuid:pk>',views.delete_my_own_request, name='delete-own-request'),
    #path('my_share_requests/edit_requests/<uuid:pk>',views.MyShareRequestUpdateView.my_share_request_update_view,name='edit-my-own-request'),
    #path('open_share_requests/',views.RequestListSharerView,name='open-share-request'),
    path('open_share_requests/<uuid:pk>',views.OpenSharerRequestDetailView.open_share_request_detail_view,name='open-share-request-detail'),
    #path('join_request/<uuid:pk>',views.confirm_request,name='confirm share'),
    #path('join_request/<uuid:pk>',views.confirm_request,name='confirm share'),
    #path('success/<uuid:pk>',name='success')
    path('my_share_requests/edit_requests/<uuid:pk>', views.MyShareRequestUpdateView.my_share_request_update_view, name='edit-my-share-request'),
    path('my_share_requests/delete_requests/<uuid:pk>', views.delete_my_share_request, name='delete-my-share-request'),
]

urlpatterns +=[
    path('my_account/',views.view_my_account, name='my-account'),
    path('edit_my_account/', views.edit_my_account_view, name='edit-my-account'),
    path('update_as_driver/', views.upgrade_as_driver, name='upgrade-as-a-driver'),

]