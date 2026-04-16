from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from django.http import HttpResponse
from .models import Lecturer, Room, Allocation, Exam, Absence
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import random


# HOME
def home(request):
    return render(request, 'home.html')


# REGISTER
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            Lecturer.objects.create(
                user=user,
                name=form.cleaned_data.get('name', ''),
                department=form.cleaned_data.get('department', ''),
                role=form.cleaned_data.get('role', 'FULL'),
                max_duties=5
            )

            messages.success(request, "Account created successfully 🎉")
            login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, "Registration failed.")

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


# DASHBOARD
@login_required
def dashboard(request):
    lecturer = Lecturer.objects.filter(user=request.user).first()

    if request.user.is_superuser:
        return redirect('/admin/')

    if not lecturer:
        messages.error(request, "Lecturer profile not found ❌")
        return redirect('home')

    if lecturer.role == 'HOD':
        allocations = Allocation.objects.values(
            'room__room_number'
        ).annotate(count=Count('id'))

        labels = [a['room__room_number'] for a in allocations]
        data = [a['count'] for a in allocations]

        total_allocations = sum(data)
        total_rooms = len(labels)
        avg = total_allocations // total_rooms if total_rooms else 0

        return render(request, 'hod_dashboard.html', {
            'labels': labels,
            'data': data,
            'total_allocations': total_allocations,
            'total_rooms': total_rooms,
            'avg': avg
        })

    duties = Allocation.objects.filter(lecturer=lecturer)\
        .select_related('exam', 'room')\
        .order_by('exam__date', 'exam__session')

    return render(request, 'faculty_dashboard.html', {
        'duties': duties,
        'total_duties': duties.count(),
        'has_duties': duties.exists()
    })


# AUTO ALLOCATION
@login_required
def auto_allocate(request, exam_id):

    if not request.user.is_superuser:
        messages.error(request, "Only Admin can perform allocation ❌")
        return redirect('dashboard')

    exam = get_object_or_404(Exam, id=exam_id)

    Allocation.objects.filter(exam=exam).delete()
    Lecturer.objects.update(assigned_duties=0)

    absent_lecturers = Absence.objects.filter(
        date=exam.date
    ).values_list('lecturer_id', flat=True)

    lecturers = list(
        Lecturer.objects.exclude(id__in=absent_lecturers)
    )

    rooms = list(Room.objects.all().order_by('room_number'))
    random.shuffle(lecturers)

    for room in rooms:
        for lecturer in lecturers:

            if lecturer.assigned_duties >= lecturer.max_duties:
                continue

            # ✅ prevents same person same session same day
            if Allocation.objects.filter(
                lecturer=lecturer,
                exam__date=exam.date,
                exam__session=exam.session
            ).exists():
                continue

            Allocation.objects.create(
                room=room,
                exam=exam,
                lecturer=lecturer
            )

            lecturer.assigned_duties += 1
            lecturer.save()
            break

    messages.success(request, "Allocation completed successfully ✅")
    return redirect(f"/allocate-result/{exam.id}/")


# FACULTY PDF
@login_required
def download_my_duties(request):
    from collections import defaultdict

    lecturer = get_object_or_404(Lecturer, user=request.user)

    allocations = sorted(
        Allocation.objects.filter(lecturer=lecturer).select_related('exam', 'room'),
        key=lambda x: (x.exam.date, 0 if x.exam.session == "1" else 1)
    )

    grouped = defaultdict(list)
    for alloc in allocations:
        grouped[alloc.exam.date].append(alloc)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_duties.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("INVIGILATOR MANAGEMENT SYSTEM", styles['Title']))
    elements.append(Paragraph("My Invigilation Duties", styles['Heading2']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Faculty: {lecturer.name}", styles['Normal']))
    elements.append(Paragraph(f"Total Duties: {len(allocations)}", styles['Normal']))
    elements.append(Spacer(1, 15))

    for date in sorted(grouped.keys()):
        elements.append(Paragraph(str(date), styles['Heading3']))
        elements.append(Spacer(1, 8))

        data = [["Room", "Session"]]

        for alloc in grouped[date]:
            session_text = "FN" if alloc.exam.session == "1" else "AN"
            data.append([alloc.room.room_number, session_text])

        table = Table(data)

        style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [colors.white, colors.HexColor("#ECF0F1")]),
            ('TEXTCOLOR', (1,1), (1,-1), colors.white),
            ('ALIGN', (1,1), (1,-1), 'CENTER'),
        ]

        for i in range(1, len(data)):
            session_value = grouped[date][i-1].exam.session

            if session_value == "1":
                style.append(('BACKGROUND', (1,i), (1,i), colors.HexColor("#3498DB")))
            else:
                style.append(('BACKGROUND', (1,i), (1,i), colors.HexColor("#E67E22")))

        table.setStyle(style)

        elements.append(table)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    return response


# HOD PDF
@login_required
def download_all_duties(request):
    from collections import defaultdict

    lecturer = Lecturer.objects.filter(user=request.user).first()

    if not request.user.is_superuser:
        if not lecturer or lecturer.role != 'HOD':
            messages.error(request, "Unauthorized ❌")
            return redirect('dashboard')

    allocations = sorted(
        Allocation.objects.select_related('room', 'lecturer', 'exam'),
        key=lambda x: (x.exam.date, 0 if x.exam.session == "1" else 1)
    )

    grouped = defaultdict(list)
    for alloc in allocations:
        key = (alloc.exam.date, alloc.exam.session)
        grouped[key].append(alloc)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="all_duties.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("INVIGILATOR MANAGEMENT SYSTEM", styles['Title']))
    elements.append(Paragraph("Full Invigilation Report", styles['Heading2']))
    elements.append(Spacer(1, 12))

    for (date, session) in sorted(grouped.keys(), key=lambda x: (x[0], 0 if x[1] == "1" else 1)):

        session_name = "Forenoon (FN)" if session == "1" else "Afternoon (AN)"

        elements.append(Paragraph(f"{date} — {session_name}", styles['Heading3']))
        elements.append(Spacer(1, 8))

        data = [["Room", "Lecturer"]]

        for alloc in grouped[(date, session)]:
            data.append([
                alloc.room.room_number,
                alloc.lecturer.name
            ])

        table = Table(data)
        table.setStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2C3E50")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ])

        elements.append(table)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    return response


# RESULT
@login_required
def allocation_result(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    allocations = Allocation.objects.filter(
        exam=exam
    ).select_related('room', 'lecturer')

    lecturer = Lecturer.objects.filter(user=request.user).first()

    return render(request, 'allocation_result.html', {
        'exam': exam,
        'allocations': allocations,
        'lecturer': lecturer
    })


# LOGOUT
def user_logout(request):
    logout(request)
    request.session.flush()
    messages.success(request, "Logged out successfully 👋")
    return redirect('home')