from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm, ProfileForm, ProfilePasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Todo
import calendar
from datetime import datetime, date, time

def home(request):
	context = {}

	if request.user.is_authenticated:
		# Get current date info
		today = date.today()
		year = int(request.GET.get('year', today.year))
		month = int(request.GET.get('month', today.month))

		# Create calendar
		cal = calendar.monthcalendar(year, month)
		month_name = calendar.month_name[month]

		# Calculate previous and next month
		if month == 1:
			prev_month, prev_year = 12, year - 1
		else:
			prev_month, prev_year = month - 1, year

		if month == 12:
			next_month, next_year = 1, year + 1
		else:
			next_month, next_year = month + 1, year

		# Get todo counts for each day in the month
		todos_in_month = Todo.objects.filter(
			user=request.user,
			date__year=year,
			date__month=month
		)

		# Create a dictionary of day -> todo count
		todo_counts = {}
		for todo in todos_in_month:
			day = todo.date.day
			todo_counts[day] = todo_counts.get(day, 0) + 1

		context.update({
			'calendar': cal,
			'month_name': month_name,
			'year': year,
			'month': month,
			'today': today,
			'prev_month': prev_month,
			'prev_year': prev_year,
			'next_month': next_month,
			'next_year': next_year,
			'todo_counts': todo_counts,
		})

	return render(request, 'home.html', context)

def register_user(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, 'Registration successful! Welcome!')
			return redirect('home')
	else:
		form = RegisterForm()

	return render(request, 'register.html', {'form': form})

def login_user(request):
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.success(request, f'Welcome back, {username}!')
				return redirect('home')
		else:
			messages.error(request, 'Invalid username or password.')
	else:
		form = AuthenticationForm()

	return render(request, 'login.html', {'form': form})

def logout_user(request):
	logout(request)
	messages.success(request, 'You have been logged out.')
	return redirect('home')

@login_required
def profile(request):
	if request.method == 'POST':
		if 'update_profile' in request.POST:
			profile_form = ProfileForm(request.POST, instance=request.user)
			password_form = ProfilePasswordForm(request.user)
			if profile_form.is_valid():
				profile_form.save()
				messages.success(request, 'Your profile has been updated.')
				return redirect('profile')
		elif 'change_password' in request.POST:
			profile_form = ProfileForm(instance=request.user)
			password_form = ProfilePasswordForm(request.user, request.POST)
			if password_form.is_valid():
				user = password_form.save()
				update_session_auth_hash(request, user)
				messages.success(request, 'Your password has been changed.')
				return redirect('profile')
		else:
			profile_form = ProfileForm(instance=request.user)
			password_form = ProfilePasswordForm(request.user)
	else:
		profile_form = ProfileForm(instance=request.user)
		password_form = ProfilePasswordForm(request.user)

	return render(request, 'profile.html', {
		'profile_form': profile_form,
		'password_form': password_form,
	})

@login_required
def day_view(request, year, month, day):
	selected_date = date(year, month, day)

	if request.method == 'POST':
		action = request.POST.get('action')

		if action == 'add':
			task = request.POST.get('task')
			time_str = request.POST.get('time')
			if task:
				task_time = None
				if time_str:
					try:
						hour, minute = map(int, time_str.split(':'))
						task_time = time(hour, minute)
					except:
						pass

				Todo.objects.create(
					user=request.user,
					date=selected_date,
					task=task,
					time=task_time
				)
				messages.success(request, 'Task added successfully!')

		elif action == 'toggle':
			todo_id = request.POST.get('todo_id')
			todo = get_object_or_404(Todo, id=todo_id, user=request.user)
			todo.completed = not todo.completed
			todo.save()

		elif action == 'delete':
			todo_id = request.POST.get('todo_id')
			todo = get_object_or_404(Todo, id=todo_id, user=request.user)
			todo.delete()
			messages.success(request, 'Task deleted successfully!')

		return redirect('day', year=year, month=month, day=day)

	# Get all todos for this day
	todos = Todo.objects.filter(user=request.user, date=selected_date)

	# Create hourly schedule from 7am to 7pm
	hours = []
	for hour in range(7, 20):  # 7am to 7pm (19:00)
		hour_time = time(hour, 0)
		# Get tasks for this hour
		hour_todos = todos.filter(time=hour_time)
		hours.append({
			'time': hour_time,
			'hour_12': hour if hour <= 12 else hour - 12,
			'period': 'AM' if hour < 12 else 'PM',
			'hour_24': hour,
			'todos': hour_todos
		})

	# Get tasks without a specific time
	unscheduled_todos = todos.filter(time__isnull=True)

	context = {
		'selected_date': selected_date,
		'todos': todos,
		'hours': hours,
		'unscheduled_todos': unscheduled_todos,
		'year': year,
		'month': month,
		'day': day,
	}

	return render(request, 'day.html', context)
