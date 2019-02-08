from .models import Order, Party
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.core.mail import send_mail
from django.utils import timezone as datetime
from datetime import datetime
import datetime
from .forms import MakeShareRequest, UpgradeAsDriverForm
from .forms import MyShareRequestUpdateForm, MakeRequest, RegisterAsDriverForm, RegisterAsUserForm, MyOwnRequestUpdateForm, EditInfoForm


def welcome(request):
    return render(request, 'welcome.html')


def index(request):
    num_sharer = Party.objects.filter(sharer_person=request.user).count()
    num_driver = Order.objects.filter(driver=request.user).count()
    num_orders = Order.objects.filter(owner=request.user).count()

    return render(request, 'index.html',
                  context={'num_orders': num_orders, 'num_sharer': num_sharer, 'num_driver': num_driver})


"""show the detail of all kind request"""


class RequestDetailView(LoginRequiredMixin, generic.DetailView):
    model = Order
    template_name = 'myapp/request_detail.html'
    context_object_name = 'order'

    def request_detail_view(request, pk):
        try:
            order = get_object_or_404(Order, pk=pk)
        except Order.DoesNotExist:
            raise Http404("Order does not exist")
        try:
            parties = Party.objects.filter(request=order).all()
        except Party.DoesNotExist:
            raise Http404("Party does not exist")
        if request.method == 'POST':
            order.driver = request.user
            order.status = 'confirm'
            order.save()
            return HttpResponseRedirect(reverse('index'))

        else:
            return render(request, 'myapp/request_detail.html', context={'order': order, 'parties': parties})


class MyOwnRequestListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'myapp/my_own_request_list.html'
    # paginate_by = 10
    context_object_name = 'requests_list'

    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user).order_by('arrival_time')


@login_required()
def my_own_request_list_can_delete(request):
    own_request = Order.objects.filter(owner=request.user)
    d = request.POST.get('delete_own_request')
    pk = request.POST.get('order_id')
    order = get_object_or_404(Order, pk=pk)
    if not d:
        order.delete()
        return HttpResponseRedirect(reverse('index'))

    else:
        return render(request, 'myapp/my_own_request_list.html', context={'requests_list': own_request})


class MyShareRequestListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'myapp/my_share_request_list.html'
    paginate_by = 10
    context_object_name = 'requests_list'

    def get_queryset(self):
        return Order.objects.filter(party__sharer_person=self.request.user).order_by('arrival_time')


class MyDriveRequestListView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'myapp/my_driving_request_list.html'
    paginate_by = 10
    context_object_name = 'requests_list'

    # 如果post就提交，保存，返回主界面//或者不返回，否则渲染list模版
    def get_queryset(self):
        return Order.objects.filter(driver=self.request.user).order_by('arrival_time')


def drive_complete_request(request):
    if request.method == 'POST':
        order_pk = request.POST.get("order_pk")
        try:
            order = get_object_or_404(Order, pk=order_pk)
            # parties = Party.objects.get()
        except Order.DoesNotExist:
            raise Http404("Order does not exist")
        try:
            parties = Party.objects.filter(request=order)
        except Order.DoesNotExist:
            raise Http404("Order does not exist")
        order.status = "complete"
        send_mail('iUber -- Request Complete',
                  'Dear passenger, your order has been complete!',
                  'pzq316@outlook.com', [order.owner.email],
                  fail_silently=False)
        for party in parties:
            send_mail('iUber -- Request Complete',
                      'Dear passenger, your order has been complete! ',
                      'pzq316@outlook.com', [party.sharer_person.email],
                      fail_silently=False)
        order.save()
        return HttpResponseRedirect(reverse('index'))

    else:
        requests_list = Order.objects.filter(driver=request.user).order_by('arrival_time')
        return render(request, 'myapp/my_driving_request_list.html', context={'requests_list': requests_list})


class RequestListDriverView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'myapp/open_order_list.html'
    context_object_name = 'requests_list'

    def get_queryset(self):
        res = Order.objects.filter(driver=None, status__exact='open').filter(
            passenger_number__lte=self.request.user.max_passenger)

        return res.exclude(owner=self.request.user).exclude(party__sharer_person=self.request.user)


"""
class RequestListSharerView(LoginRequiredMixin, generic.ListView):
    model = Order
    template_name = 'myapp/open_share_order_list.html'
    paginate_by = 10
    context_object_name = 'requests_list'
    # def confirm_share(self,request):
    #     dest = request.POST.get('destination')
    #     arrival = request.POST.get('arrival_time')
    #     pass_num = request.POST.get('passenger_number')
    #
    #     s = request.POST.get('search')
    #     if not s:
    #         return render(request, 'myapp/make_share_request.html')
    #     else:
    #         requests_list = Order.objects.filter(destination=dest,arrival_time=arrival)
    #     return render(request, 'myapp/open_share_order_list.html', {'requests_list': requests_list})
    def get_queryset(self):
        return Order.objects.filter(driver=None, status__exact='open',is_shared__exact=True,
                                    passenger_number__lte=self.request.user.max_passenger)
        # return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
"""


class OrderConfirmView(LoginRequiredMixin, generic.DetailView):
    # model = Book

    def order_confirm_view(request, pk):
        try:
            order = get_object_or_404(Order, pk=pk)
        except Order.DoesNotExist:
            raise Http404("Order does not exist")
        try:
            parties = Party.objects.filter(request=order)
        except Party.DoesNotExist:
            raise Http404("Party does not exist")

        if request.method == 'POST':
            order.driver = request.user
            order.status = 'confirm'
            send_mail('iUber -- Request Confirmation',
                      'Dear passenger, your order has been confirmed!',
                      'pzq316@outlook.com', [order.owner.email],
                      fail_silently=False)
            for party in parties:
                send_mail('iUber -- Request Confirmation',
                          'Dear passenger, your order has been confirmed! ',
                          'pzq316@outlook.com', [party.sharer_person.email],
                          fail_silently=False)

            order.save()
            return HttpResponseRedirect(reverse('index'))

        else:
            return render(request, 'myapp/open_order_detail.html', context={'order': order})


"""
@permission_required('myapp.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst=get_object_or_404(BookInstance, pk = pk)
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('index'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'myapp/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})
"""


def registerAsUser(request):
    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        form = RegisterAsUserForm(request.POST)
        if form.is_valid():
            form.save()
            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
    else:
        form = RegisterAsUserForm()

    return render(request, 'myapp/register.html', context={'form': form, 'next': redirect_to,"valid_flag":True})


def registerAsDriver(request):
    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        form = RegisterAsDriverForm(request.POST)

        if form.is_valid():
            if form.full_name is None or form.vehicle_type is None or form.license_num is None or form.max_passenger is None:
                return render(request,'myapp/register.html',content_type={'form':form,"valid_flag":False})
            form.save()
            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
    else:
        form = RegisterAsDriverForm()

    return render(request, 'myapp/register.html', context={'form': form, "valid_flag":True})


class MyOwnRequestUpdateView(LoginRequiredMixin, generic.DetailView):
    model = Order

    def my_own_request_update_view(request, pk):
        order = get_object_or_404(Order, pk=pk)
        whether_share = request.POST.get("is_shared")
        old_destination = order.destination
        old_arrival_time = order.arrival_time
        old_passenger_num = order.passenger_number
        old_own_pass_num = order.own_pass_num
        if request.method == 'POST':
            form = MyOwnRequestUpdateForm(request.POST)
            # form.arrival_time=order.arrival_time
            if form.is_valid():
                order.destination = form.cleaned_data['destination']
                order.own_pass_num = form.cleaned_data['own_pass_num']
                order.arrival_time = form.cleaned_data['arrival_time']
                order.special_request = form.cleaned_data['special_request']
                order.special_vehicle_type = form.cleaned_data['special_vehicle_type']
                if whether_share == 'yes':
                    order.is_shared = True
                else:
                    order.is_shared = False

                if old_arrival_time != order.arrival_time or old_destination != order.destination or order.is_shared == False:
                    # if not order.sharer:
                    try:
                        party = Party.objects.filter(request=order).all()
                    except Order.DoesNotExist:
                        raise Http404("Party does not exist")
                    party.delete()
                    order.passenger_number = order.own_pass_num  # 人数变成自己的人数
                else:  # 人数更新
                    order.passenger_number = order.passenger_number - old_own_pass_num + order.own_pass_num
                order.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            form = MyOwnRequestUpdateForm()
            return render(request, 'myapp/update_my_own_request.html', context={'form': form, 'order': order})


class MyShareRequestUpdateView(LoginRequiredMixin, generic.DetailView):
    model = Order

    def my_share_request_update_view(request, pk):
        order = get_object_or_404(Order, pk=pk)
        party = Party.objects.get(sharer_person=request.user, request=order)
        old_num = party.share_pass_num

        if request.method == 'POST':
            form = MyShareRequestUpdateForm(request.POST)

            if form.is_valid():
                party.share_pass_num = form.cleaned_number()  # form.cleaned_data['share_pass_num']
                order.passenger_number = order.passenger_number + party.share_pass_num - old_num
                order.save()
                party.save()
                # if redirect_to:
                #     return redirect(redirect_to)
                # else:
                #     return redirect('/')
            return HttpResponseRedirect(reverse('index'))

        else:
            form = MyOwnRequestUpdateForm()
            return render(request, 'myapp/update_my_share_request.html', context={'form': form, 'order': party})


@login_required()
def make_a_request(request):
    # order=get_object_or_404(Order, pk = pk)
    order = Order()
    valid_flag = True
    if request.method == 'POST':
        form = MakeRequest(request.POST)
        whether_share = request.POST.get("is_shared")
        valid_flag = False
        if form.is_valid():
            # valid_flag = True
            order.destination = form.cleaned_data['destination']
            order.arrival_time = form.cleaned_data['arrival_time']
            order.arrival_time = form.cleaned_data['arrival_time']
            now = datetime.datetime.now()
            if order.arrival_time < now:
                return render(request, 'myapp/request.html', {'form': form, 'valid_flag': False})

            order.passenger_number = form.cleaned_data['passenger_number']
            order.own_pass_num = order.passenger_number
            order.special_request = form.cleaned_data['special_request']
            order.special_vehicle_type = form.cleaned_data['special_vehicle_type']
            # order.is_shared = form.cleaned_data['is_shared']
            if whether_share == "yes":
                order.is_shared = True
            else:
                order.is_shared = False
            order.status = 'open'
            order.owner = request.user
            order.save()
            return HttpResponseRedirect(reverse('index'))
        # return render(request, 'myapp/request.html', {'form': form, 'valid_flag': valid_flag})
    else:
        form = MakeRequest()
    return render(request, 'myapp/request.html', {'form': form, 'valid_flag': valid_flag})


@login_required()
def make_a_share_request(request):
    # dest = request.POST.get('destination')
    # #arrival = request.POST.get('arrival_time')
    # share_pass_num = request.POST.get('share_pass_num')
    # earliest_arrival = request.POST.get('earliest_arrival')
    # latest_arrival = request.POST.get('latest_arrival')
    valid_flag = True
    # party = Party()
    s = request.POST.get('search')
    if not s:
        form = MakeShareRequest()
        return render(request, 'myapp/make_share_request.html', {'form': form, 'valid_flag': True})
    else:
        form = MakeShareRequest(request.POST)
        if form.is_valid():
            dest = form.cleaned_data['destination']
            earliest_arrival = form.cleaned_data['earliest_arrival']
            latest_arrival = form.cleaned_data['latest_arrival']
            share_pass_num = form.cleaned_data['share_pass_num']
            if latest_arrival < datetime.datetime.now() or earliest_arrival > latest_arrival:
                return render(request, 'myapp/make_share_request.html', {'form': form, 'valid_flag': False})

            requests_list = Order.objects.filter(is_shared__exact=True, destination=dest,
                                                 arrival_time__gte=earliest_arrival,
                                                 arrival_time__lte=latest_arrival).exclude(
                party__sharer_person=request.user).exclude(
                driver=request.user).all()  # ,passenger_number__lte=6-party.share_pass_num)
            return render(request, 'myapp/open_share_order_list.html',
                          {'requests_list': requests_list, 'share_pass_num': share_pass_num})
        return render(request, 'myapp/make_share_request.html', {'form': form, 'valid_flag': False})


class OpenSharerRequestDetailView(LoginRequiredMixin, generic.DetailView):
    # model = Order
    template_name = 'myapp/open_share_order_detail.html'
    context_object_name = 'requests_list'

    def open_share_request_detail_view(request, pk):
        # pass_num = request.POST.get('passenger_number')
        pass_num = request.POST.get('share_pass_num')
        submit = request.POST.get('s')
        pass_num_int = int(pass_num)

        try:
            order = get_object_or_404(Order, pk=pk)
        except Order.DoesNotExist:
            raise Http404("Order does not exist")

        # if request.method == 'POST':
        if submit:
            party = Party()
            # order.sharer.add(request.user)
            # order.objects.passenger_number = pass_num + order.objects.passenger_number
            party.request = order
            party.share_pass_num = pass_num
            party.sharer_name = request.user.username
            order.passenger_number = order.passenger_number + pass_num_int
            # order.sharer.add(request.user)
            party.sharer_person = request.user
            party.sharer_person_id = request.user.id
            party.save()
            order.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'myapp/open_share_order_detail.html', context={'order': order})


"""
@login_required()
def confirm_request(request,pk):
    # dest = request.POST.get('destination')
    # arrival = request.POST.get('arrival_time')
    # pass_num = request.POST.get('passenger_number')
    #
    # s = request.POST.get('search')
    # if not s:
    #     return render(request, 'myapp/make_share_request.html')
    # else:
    #     requests_list = Order.objects.filter(destination=dest,arrival_time=arrival)
    #     return render(request, 'myapp/open_share_order_list.html', {'requests_list': requests_list})
    try:
        order = get_object_or_404(Order, pk=pk)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")

    if request.method == 'POST':
        try:
            party = Party.objects.get(request=None,sharer_person=request.user)
        except Order.DoesNotExist:
            raise Http404("Order does not exist")
        party.request = order
        order.passenger_number += party.share_pass_num
        order.sharer.add(request.user)
        order.save()
        party.save()
        return HttpResponseRedirect(reverse('index'))
        #return render(request, 'myapp/success.html',)

    else:
        RequestListSharerView.as_view()
        return render(request, 'myapp/open_share_order_detail.html', context={'order': order})
"""


@login_required()
def delete_my_own_request(request, pk):
    try:
        order = get_object_or_404(Order, pk=pk)
        # parties = Party.objects.get()
    except Order.DoesNotExist:
        raise Http404("Order does not exist")
    # if order.status!='open': //订单不是open的异常

    if request.method == 'POST':
        order.delete()
        return HttpResponseRedirect(reverse('index'))
        # return render(request, 'myapp/success.html',)
    else:
        return render(request, 'myapp/my_own_request_detail.html', context={'order': order})


@login_required()
def delete_my_share_request(request, pk):
    try:
        order = get_object_or_404(Order, pk=pk)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")
    # if order.status!='open': //订单不是open的异常

    if request.method == 'POST':
        try:
            party = Party.objects.get(request=order, sharer_person=request.user)
        except Party.DoesNotExist:
            raise Http404("Party does not exist")
        order.passenger_number = order.passenger_number - party.share_pass_num
        # order.sharer.remove(request.user)
        order.save()
        party.delete()
        return HttpResponseRedirect(reverse('index'))
        # return render(request, 'myapp/success.html',)
    else:
        return render(request, 'myapp/my_own_request_detail.html', context={'order': order})


@login_required()
def view_my_account(request):  # add full name
    return render(request, 'myapp/my_account.html')


@login_required()
def edit_my_account_view(request):
    if request.method == 'POST':
        form = EditInfoForm(request.POST)

        if form.is_valid():
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.vehicle_type = form.cleaned_data['vehicle_type']
            request.user.max_passenger = form.cleaned_data['max_passenger']
            request.user.license_num = form.cleaned_data['license_num']
            request.user.special_vehicle_info = form.cleaned_data['special_vehicle_info']
            request.user.save()

        return HttpResponseRedirect(reverse('index'))

    else:
        form = EditInfoForm()
        return render(request, 'myapp/edit_my_account.html', context={'form': form, })


@login_required()
def upgrade_as_driver(request):
    if request.method == 'POST':
        form = UpgradeAsDriverForm(request.POST)

        if form.is_valid():
            request.user.vehicle_type = form.cleaned_data['vehicle_type']
            request.user.max_passenger = form.cleaned_data['max_passenger']
            request.user.license_num = form.cleaned_data['license_num']
            request.user.full_name = form.cleaned_data['full_name']
            request.user.special_vehicle_info = form.cleaned_data['special_vehicle_info']
            request.user.is_driver = True
            request.user.save()
            return HttpResponseRedirect(reverse('index'))
        return render(request, 'myapp/upgrade_as_driver.html', context={'form': form, 'valid_flag': False})
    else:
        form = EditInfoForm()
        return render(request, 'myapp/upgrade_as_driver.html', context={'form': form, 'valid_flag': True})
