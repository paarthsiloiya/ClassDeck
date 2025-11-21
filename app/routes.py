import os
import json
from datetime import datetime
from flask import render_template, redirect, url_for, session, request, flash
from flask_login import current_user, login_user, logout_user, login_required
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth.transport.requests
from app import app, db, login
from app.models import User, Course, CourseTag, ItemTag

# Helper for file icons
def get_file_icon(mime_type, title=None):
    if not mime_type:
        return 'file text-gray-500'
    
    mime_type = mime_type.lower()
    if 'pdf' in mime_type:
        return 'file-pdf text-red-500'
    elif 'image' in mime_type:
        return 'file-image text-purple-500'
    elif 'video' in mime_type:
        return 'file-video text-red-600'
    elif 'audio' in mime_type:
        return 'file-audio text-yellow-500'
    elif 'sheet' in mime_type or 'excel' in mime_type or 'spreadsheet' in mime_type:
        return 'file-excel text-green-500'
    elif 'presentation' in mime_type or 'powerpoint' in mime_type or 'slides' in mime_type:
        return 'file-powerpoint text-orange-500'
    elif 'document' in mime_type or 'word' in mime_type:
        return 'file-word text-blue-500'
    elif 'form' in mime_type:
        return 'file-alt text-purple-600'
    else:
        return 'file text-gray-500'

app.jinja_env.globals.update(get_file_icon=get_file_icon)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
    courses = []
    if current_user.is_authenticated:
        # Build credentials from stored user data
        credentials = Credentials(
            token=current_user.access_token,
            refresh_token=current_user.refresh_token,
            token_uri=current_user.token_uri,
            client_id=current_user.client_id,
            client_secret=current_user.client_secret,
            scopes=current_user.scopes.split(',') if current_user.scopes else []
        )

        try:
            # Get courses
            classroom_service = build('classroom', 'v1', credentials=credentials)
            results = classroom_service.courses().list(studentId='me').execute()
            google_courses = results.get('courses', [])
            
            # Merge with local data
            for g_course in google_courses:
                local_course = Course.query.filter_by(user_id=current_user.id, google_course_id=g_course['id']).first()
                
                # Create a display object (dict)
                display_course = g_course.copy()
                display_course['is_archived'] = False
                
                # Determine if archived (Google state or Local override)
                if g_course.get('courseState') == 'ARCHIVED':
                    display_course['is_archived'] = True
                
                if local_course:
                    if local_course.custom_name:
                        display_course['name'] = local_course.custom_name
                    if local_course.custom_section:
                        display_course['section'] = local_course.custom_section
                    if local_course.custom_code:
                        display_course['enrollmentCode'] = local_course.custom_code # Override enrollment code for display
                    if local_course.is_archived:
                        display_course['is_archived'] = True
                    # Add other custom fields if needed for template
                    display_course['custom_banner'] = local_course.custom_banner
                    display_course['custom_icon'] = local_course.custom_icon
                    display_course['custom_teacher_name'] = local_course.custom_teacher_name
                    display_course['cached_teacher_name'] = local_course.cached_teacher_name
                    display_course['display_order'] = local_course.display_order
                
                # Fetch teacher name if missing
                if not display_course.get('custom_teacher_name') and not display_course.get('cached_teacher_name'):
                    try:
                        # We need to fetch the teacher profile. 
                        # Note: This can be slow for many courses. Ideally, do this asynchronously or in batch.
                        # For now, we'll do it on demand and cache it.
                        owner_id = g_course.get('ownerId')
                        if owner_id:
                            user_profile = classroom_service.userProfiles().get(userId=owner_id).execute()
                            teacher_name = user_profile.get('name', {}).get('fullName')
                            
                            if not local_course:
                                local_course = Course(user_id=current_user.id, google_course_id=g_course['id'])
                                db.session.add(local_course)
                            
                            local_course.cached_teacher_name = teacher_name
                            db.session.commit()
                            display_course['cached_teacher_name'] = teacher_name
                    except HttpError as e:
                        if e.resp.status == 403:
                             # Check for missing scopes
                            required_scopes = set(app.config['GOOGLE_SCOPES'])
                            current_scopes = set(current_user.scopes.split(',')) if current_user.scopes else set()
                            
                            missing_scopes = required_scopes - current_scopes
                            if missing_scopes:
                                print(f"Missing scopes for teacher fetch: {missing_scopes}")
                                logout_user()
                                flash('New permissions are required to view teacher names. Please log in again.', 'info')
                                return redirect(url_for('login'))
                        print(f"Error fetching teacher for {g_course['id']}: {e}")
                    except Exception as e:
                        print(f"Error fetching teacher for {g_course['id']}: {e}")

                # Final Teacher Name Logic
                display_course['teacher_name'] = display_course.get('custom_teacher_name') or display_course.get('cached_teacher_name') or 'Unknown Teacher'

                if not display_course['is_archived']:
                    courses.append(display_course)
                    
        except Exception as e:
            # Token might be expired and refresh failed, or other API error
            flash(f'Error fetching courses: {str(e)}', 'error')
            # Optionally force re-login if token is invalid
            
    # Sort courses by display_order
    courses.sort(key=lambda x: x.get('display_order', 0))
            
    return render_template('index.html', title='Home', courses=courses)

@app.route('/archived')
@login_required
def archived_courses():
    courses = []
    # Build credentials from stored user data
    credentials = Credentials(
        token=current_user.access_token,
        refresh_token=current_user.refresh_token,
        token_uri=current_user.token_uri,
        client_id=current_user.client_id,
        client_secret=current_user.client_secret,
        scopes=current_user.scopes.split(',') if current_user.scopes else []
    )

    try:
        # Get courses
        classroom_service = build('classroom', 'v1', credentials=credentials)
        results = classroom_service.courses().list(studentId='me').execute()
        google_courses = results.get('courses', [])
        
        # Merge with local data
        for g_course in google_courses:
            local_course = Course.query.filter_by(user_id=current_user.id, google_course_id=g_course['id']).first()
            
            display_course = g_course.copy()
            display_course['is_archived'] = False
            
            if g_course.get('courseState') == 'ARCHIVED':
                display_course['is_archived'] = True
            
            if local_course:
                if local_course.custom_name: display_course['name'] = local_course.custom_name
                if local_course.custom_section: display_course['section'] = local_course.custom_section
                if local_course.custom_banner: display_course['custom_banner'] = local_course.custom_banner
                if local_course.is_archived: display_course['is_archived'] = True
                display_course['teacher_name'] = local_course.custom_teacher_name or local_course.cached_teacher_name
            
            if display_course['is_archived']:
                courses.append(display_course)
                
    except Exception as e:
        flash(f'Error fetching archived courses: {str(e)}', 'error')
        
    return render_template('index.html', title='Archived Classes', courses=courses, is_archived_view=True)

@app.route('/missing')
@login_required
def missing_assignments():
    assignments = []
    
    # Build credentials
    credentials = Credentials(
        token=current_user.access_token,
        refresh_token=current_user.refresh_token,
        token_uri=current_user.token_uri,
        client_id=current_user.client_id,
        client_secret=current_user.client_secret,
        scopes=current_user.scopes.split(',') if current_user.scopes else []
    )
    
    try:
        service = build('classroom', 'v1', credentials=credentials)
        
        # 1. Get all active courses
        results = service.courses().list(studentId='me', courseStates=['ACTIVE']).execute()
        courses = results.get('courses', [])
        
        if not courses:
             return render_template('missing_assignments.html', title='Missing Assignments', assignments=[])

        # Prepare data structures for batch results
        all_course_work = {} # course_id -> [work]
        all_submissions = {} # course_id -> [submission]
        
        # Callbacks
        def cw_callback(request_id, response, exception):
            if exception:
                print(f"Error fetching coursework for {request_id}: {exception}")
            else:
                all_course_work[request_id] = response.get('courseWork', [])

        def sub_callback(request_id, response, exception):
            if exception:
                print(f"Error fetching submissions for {request_id}: {exception}")
            else:
                all_submissions[request_id] = response.get('studentSubmissions', [])

        # 2. Batch fetch CourseWork
        batch_cw = service.new_batch_http_request(callback=cw_callback)
        for course in courses:
            batch_cw.add(service.courses().courseWork().list(courseId=course['id']), request_id=course['id'])
        batch_cw.execute()
        
        # 3. Batch fetch Submissions
        batch_sub = service.new_batch_http_request(callback=sub_callback)
        for course in courses:
            batch_sub.add(service.courses().courseWork().studentSubmissions().list(
                courseId=course['id'],
                courseWorkId='-',
                userId='me',
                states=['CREATED', 'RECLAIMED_BY_STUDENT']
            ), request_id=course['id'])
        batch_sub.execute()

        # 4. Process Data
        now = datetime.utcnow()
        
        for course in courses:
            c_id = course['id']
            course_work = all_course_work.get(c_id, [])
            submissions = all_submissions.get(c_id, [])
            
            if not course_work:
                continue
                
            # Map submissions to coursework ID
            submission_map = {s['courseWorkId']: s for s in submissions}
            
            for work in course_work:
                if work['id'] in submission_map:
                    # It is not turned in. Check due date.
                    if 'dueDate' in work:
                        # Parse due date
                        due = work['dueDate'] # {year, month, day}
                        time = work.get('dueTime', {'hours': 23, 'minutes': 59})
                        
                        try:
                            due_dt = datetime(due['year'], due['month'], due['day'], time.get('hours', 0), time.get('minutes', 0))
                            
                            if due_dt < now:
                                # It is missing!
                                assignment = work.copy()
                                assignment['courseName'] = course['name']
                                assignment['dueDate'] = due_dt.strftime('%Y-%m-%d %H:%M')
                                assignments.append(assignment)
                        except ValueError:
                            continue

    except Exception as e:
        flash(f'Error fetching missing assignments: {str(e)}', 'error')
    
    return render_template('missing_assignments.html', title='Missing Assignments', assignments=assignments)

@app.route('/course/<course_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    # Find or create local course record
    course = Course.query.filter_by(user_id=current_user.id, google_course_id=course_id).first()
    if not course:
        course = Course(user_id=current_user.id, google_course_id=course_id)
        db.session.add(course)
    
    if request.method == 'POST':
        course.custom_name = request.form.get('custom_name')
        course.custom_section = request.form.get('custom_section')
        course.custom_code = request.form.get('custom_code')
        course.custom_banner = request.form.get('custom_banner')
        course.custom_teacher_name = request.form.get('custom_teacher_name')
        try:
            course.display_order = int(request.form.get('display_order', 0))
        except ValueError:
            course.display_order = 0
            
        course.is_archived = 'is_archived' in request.form
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('index'))
        
    # For GET, we might want to fetch the original Google name to show as placeholder
    # But for now, let's just show the form with current local values
    return render_template('edit_course.html', course=course, google_course_id=course_id)

@app.route('/course/<course_id>/tags', methods=['POST'])
@login_required
def create_tag(course_id):
    # Ensure local course exists
    course = Course.query.filter_by(user_id=current_user.id, google_course_id=course_id).first()
    if not course:
        course = Course(user_id=current_user.id, google_course_id=course_id)
        db.session.add(course)
        db.session.commit() # Commit to get ID
    
    # Check limit
    if len(course.tags) >= 6:
        flash('Limit of 6 tags per class reached.', 'error')
        return redirect(url_for('course_stream', course_id=course_id))
        
    name = request.form.get('name')
    color = request.form.get('color', 'blue')
    
    if name:
        tag = CourseTag(course_id=course.id, name=name, color=color)
        db.session.add(tag)
        try:
            db.session.commit()
            flash('Tag created!', 'success')
        except:
            db.session.rollback()
            flash('Tag already exists.', 'error')
            
    return redirect(url_for('course_stream', course_id=course_id))

@app.route('/course/<course_id>/tags/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(course_id, tag_id):
    tag = CourseTag.query.get_or_404(tag_id)
    # Verify ownership via course
    course = Course.query.get(tag.course_id)
    if course.user_id != current_user.id or course.google_course_id != course_id:
        flash('Unauthorized', 'error')
        return redirect(url_for('index'))
        
    db.session.delete(tag)
    db.session.commit()
    flash('Tag deleted.', 'success')
    return redirect(url_for('course_stream', course_id=course_id))

@app.route('/course/<course_id>/items/<item_id>/tags', methods=['POST'])
@login_required
def toggle_item_tag(course_id, item_id):
    tag_id = request.form.get('tag_id')
    if not tag_id:
        return 'Missing tag_id', 400
        
    tag = CourseTag.query.get(int(tag_id))
    if not tag:
        return 'Tag not found', 404
        
    # Check if already assigned
    assignment = ItemTag.query.filter_by(tag_id=tag.id, google_item_id=item_id).first()
    
    if assignment:
        db.session.delete(assignment)
        action = 'removed'
    else:
        assignment = ItemTag(tag_id=tag.id, google_item_id=item_id)
        db.session.add(assignment)
        action = 'added'
        
    db.session.commit()
    
    return redirect(url_for('course_stream', course_id=course_id))

@app.route('/course/<course_id>')
@login_required
def course_stream(course_id):
    # Build credentials
    credentials = Credentials(
        token=current_user.access_token,
        refresh_token=current_user.refresh_token,
        token_uri=current_user.token_uri,
        client_id=current_user.client_id,
        client_secret=current_user.client_secret,
        scopes=current_user.scopes.split(',') if current_user.scopes else []
    )
    
    # Force refresh if needed (though google-auth usually handles this)
    if credentials.expired:
        request_adapter = google.auth.transport.requests.Request()
        credentials.refresh(request_adapter)
        # Update DB with new token
        current_user.access_token = credentials.token
        db.session.commit()
    
    service = build('classroom', 'v1', credentials=credentials)
    
    # Fetch Course Details (for banner/name)
    try:
        google_course = service.courses().get(id=course_id).execute()
    except Exception as e:
        flash(f'Error fetching course: {str(e)}', 'error')
        return redirect(url_for('index'))

    # Apply local overrides
    local_course = Course.query.filter_by(user_id=current_user.id, google_course_id=course_id).first()
    course = google_course.copy()
    
    tags = []
    item_tags_map = {}

    if local_course:
        if local_course.custom_name: course['name'] = local_course.custom_name
        if local_course.custom_section: course['section'] = local_course.custom_section
        if local_course.custom_banner: course['custom_banner'] = local_course.custom_banner
        if local_course.custom_code: course['enrollmentCode'] = local_course.custom_code
        
        tags = local_course.tags
        tag_ids = [t.id for t in tags]
        if tag_ids:
            assignments = ItemTag.query.filter(ItemTag.tag_id.in_(tag_ids)).all()
            for a in assignments:
                if a.google_item_id not in item_tags_map:
                    item_tags_map[a.google_item_id] = []
                tag_obj = next((t for t in tags if t.id == a.tag_id), None)
                if tag_obj:
                    item_tags_map[a.google_item_id].append(tag_obj)
    
    # Fetch Stream Items
    stream_items = []
    
    # Debug: Print current scopes
    print(f"Current User Scopes: {current_user.scopes}")

    try:
        # 1. Announcements
        announcements = service.courses().announcements().list(courseId=course_id).execute().get('announcements', [])
        for a in announcements:
            a['type'] = 'announcement'
            stream_items.append(a)
            
        # 2. CourseWork (Assignments, Questions)
        coursework = service.courses().courseWork().list(courseId=course_id).execute().get('courseWork', [])
        for w in coursework:
            w['type'] = 'assignment' # or 'question' based on workType
            stream_items.append(w)
            
        # 3. CourseWorkMaterials
        materials = service.courses().courseWorkMaterials().list(courseId=course_id).execute().get('courseWorkMaterial', [])
        for m in materials:
            m['type'] = 'material'
            stream_items.append(m)
            
    except HttpError as e:
        if e.resp.status == 403:
            # Check for missing scopes
            required_scopes = set(app.config['GOOGLE_SCOPES'])
            current_scopes = set(current_user.scopes.split(',')) if current_user.scopes else set()
            
            missing_scopes = required_scopes - current_scopes
            if missing_scopes:
                print(f"Missing scopes: {missing_scopes}")
                logout_user()
                flash('New permissions are required. Please log in again to grant them.', 'info')
                return redirect(url_for('login'))
                
        flash(f'Error fetching stream: {str(e)}', 'warning')
    except Exception as e:
        flash(f'Error fetching stream: {str(e)}', 'warning')

    # Sort by creation time (newest first)
    # Note: Different items have different time fields (creationTime, updateTime)
    def get_sort_time(item):
        return item.get('creationTime') or item.get('updateTime') or '1970-01-01T00:00:00.000Z'
        
    stream_items.sort(key=get_sort_time, reverse=True)

    return render_template('course_stream.html', course=course, stream_items=stream_items, tags=tags, item_tags_map=item_tags_map)

@app.route('/sync_calendar')
@login_required
def sync_calendar():
    # Placeholder for calendar sync logic
    # 1. Fetch assignments from Google Classroom
    # 2. Check if they exist in Google Calendar
    # 3. If not, add them
    
    flash('Calendar sync feature coming soon!', 'info')
    return redirect(url_for('index'))

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    flow = Flow.from_client_secrets_file(
        app.config['GOOGLE_CLIENT_SECRETS_FILE'],
        scopes=app.config['GOOGLE_SCOPES']
    )
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent' # Force consent screen to ensure new scopes are granted
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        app.config['GOOGLE_CLIENT_SECRETS_FILE'],
        scopes=app.config['GOOGLE_SCOPES'],
        state=state
    )
    flow.redirect_uri = url_for('callback', _external=True)

    authorization_response = request.url
    # Allow for scope changes/upgrades
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    
    # Get user info
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    
    google_id = user_info.get('id')
    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')

    # Check if user exists
    user = User.query.filter_by(google_id=google_id).first()
    
    if not user:
        user = User(google_id=google_id, email=email)
    
    # Update user info and tokens
    user.name = name
    user.picture = picture
    user.access_token = credentials.token
    user.refresh_token = credentials.refresh_token
    user.token_uri = credentials.token_uri
    user.client_id = credentials.client_id
    user.client_secret = credentials.client_secret
    user.scopes = ','.join(credentials.scopes) if credentials.scopes else ''
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user, remember=True)

    flash('Successfully logged in!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
