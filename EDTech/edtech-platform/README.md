# 🎓 EduPlatform — Django EdTech Backend

A production-ready EdTech backend (inspired by Physics Wallah / Unacademy)
built with **Django + PostgreSQL + Redis + Razorpay + AWS S3 + WebSockets**.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 + Django REST Framework |
| Database | PostgreSQL |
| Cache / Queue Broker | Redis |
| Background Tasks | Celery + Celery Beat |
| Real-time (Live Classes) | Django Channels + WebSockets |
| File Storage | AWS S3 |
| Payments | Razorpay |
| Auth | Token Authentication + JWT |
| Deployment | Docker + Nginx + Daphne |
| Error Tracking | Sentry |

---

## 📁 Project Structure

```
edtech-platform/
│
├── config/               # Django project settings, URLs, ASGI, Celery
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py           # WebSocket support
│   ├── wsgi.py
│   └── celery.py
│
├── courses/              # Courses, Sections, Lessons, Enrollments, Reviews
├── payments/             # Razorpay integration, Orders, Payments
├── users/                # User profiles, Auth (register/login/logout)
├── videos/               # AWS S3 video upload & management
├── live_classes/         # Live class scheduling, WebSocket consumers, Chat
├── notifications/        # In-app notifications, Email signals
│
├── templates/
│   └── emails/           # HTML email templates
│
├── Dockerfile
├── docker-compose.yml    # Full stack: Django + DB + Redis + Celery + Nginx
├── nginx.conf
├── setup.sh              # One-click local setup
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start (Local Development)

### Option A — Automatic Setup Script

```bash
git clone <your-repo-url>
cd edtech-platform
bash setup.sh
```

### Option B — Manual Setup

```bash
# 1. Clone and enter project
git clone <your-repo-url>
cd edtech-platform

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# ✏️  Edit .env with your credentials

# 5. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE edtech_db;"

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Run server
python manage.py runserver
```

---

## 🐳 Docker Deployment

```bash
# Copy and fill in your environment variables
cp .env.example .env

# Build and start all services
docker-compose up --build -d

# Check running containers
docker-compose ps

# View logs
docker-compose logs -f web

# Run migrations inside container
docker-compose exec web python manage.py migrate

# Create superuser inside container
docker-compose exec web python manage.py createsuperuser
```

---

## 🌐 API Endpoints Reference

### Authentication
| Method | URL | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login (get token) |
| POST | `/api/auth/logout/` | Logout (delete token) |
| GET | `/api/auth/profile/` | Get current user profile |
| PATCH | `/api/auth/profile/` | Update profile |
| POST | `/api/auth/change-password/` | Change password |

### Courses
| Method | URL | Description |
|---|---|---|
| GET | `/api/v1/courses/` | List all published courses |
| GET | `/api/v1/courses/?search=python` | Search courses |
| GET | `/api/v1/courses/?category=math` | Filter by category |
| POST | `/api/v1/courses/` | Create course (instructor only) |
| GET | `/api/v1/courses/{id}/` | Course detail with sections |
| POST | `/api/v1/courses/{id}/enroll/` | Enroll (free courses) |
| POST | `/api/v1/courses/{id}/review/` | Add review |
| GET | `/api/v1/enrollments/` | My enrolled courses |
| PATCH | `/api/v1/enrollments/{id}/update_progress/` | Update progress |

### Payments (Razorpay)
| Method | URL | Description |
|---|---|---|
| POST | `/api/payments/orders/create/` | Create Razorpay order |
| POST | `/api/payments/orders/verify/` | Verify payment signature |
| GET | `/api/payments/orders/` | My payment history |

### Live Classes
| Method | URL | Description |
|---|---|---|
| GET | `/api/live/` | List upcoming live classes |
| POST | `/api/live/` | Create live class (instructor) |
| GET | `/api/live/{id}/` | Live class detail + chat |
| POST | `/api/live/{id}/go-live/` | Start live class |
| POST | `/api/live/{id}/end/` | End live class |
| GET | `/api/live/{id}/participants/` | Current participants |
| GET | `/api/live/{id}/chat/` | Chat history |

### Videos
| Method | URL | Description |
|---|---|---|
| POST | `/api/v1/videos/upload/` | Upload video to S3 |
| DELETE | `/api/v1/videos/{id}/delete_video/` | Delete video |

### Notifications
| Method | URL | Description |
|---|---|---|
| GET | `/api/v1/notifications/` (via router) | All notifications |
| GET | `/api/v1/notifications/unread/` | Unread notifications |
| PATCH | `/api/v1/notifications/{id}/read/` | Mark as read |
| PATCH | `/api/v1/notifications/mark_all_read/` | Mark all as read |

---

## 🔌 WebSocket — Live Class

Connect to a live class room using WebSockets:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live-class/<live_class_id>/');

ws.onopen = () => console.log('Connected to live class!');

// Send chat message
ws.send(JSON.stringify({ type: 'chat', message: 'Hello everyone!' }));

// Send WebRTC offer (video streaming)
ws.send(JSON.stringify({ type: 'webrtc_offer', offer: sdpOffer }));

// Raise hand
ws.send(JSON.stringify({ type: 'raise_hand', raised: true }));

// Handle incoming events
ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    switch (data.type) {
        case 'chat':          handleChatMessage(data); break;
        case 'user_joined':   handleUserJoined(data);  break;
        case 'user_left':     handleUserLeft(data);    break;
        case 'webrtc_offer':  handleOffer(data);       break;
        case 'webrtc_answer': handleAnswer(data);      break;
        case 'ice_candidate': handleICE(data);         break;
        case 'raise_hand':    handleRaiseHand(data);   break;
    }
};
```

---

## 💳 Razorpay Payment Flow

```
1.  Frontend calls POST /api/payments/orders/create/ → gets razorpay_order_id
2.  Frontend opens Razorpay checkout popup with razorpay_order_id
3.  User completes payment on Razorpay
4.  Razorpay returns: razorpay_payment_id + razorpay_signature
5.  Frontend calls POST /api/payments/orders/verify/
6.  Backend verifies signature → enrolls student → sends receipt email
```

### Frontend Example (JavaScript)

```javascript
// Step 1: Create order
const { razorpay_order_id, amount, key } = await fetch('/api/payments/orders/create/', {
    method: 'POST',
    headers: { 'Authorization': `Token ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ course_id: courseId }),
}).then(r => r.json());

// Step 2: Open Razorpay checkout
const rzp = new Razorpay({
    key,
    amount,
    currency: 'INR',
    order_id: razorpay_order_id,
    handler: async (response) => {
        // Step 3: Verify payment
        await fetch('/api/payments/orders/verify/', {
            method: 'POST',
            headers: { 'Authorization': `Token ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify(response),
        });
        alert('Payment successful! You are now enrolled.');
    },
});
rzp.open();
```

---

## ⚙️ Environment Variables Guide

| Variable | Description | Example |
|---|---|---|
| `DEBUG` | Dev/prod mode | `False` |
| `SECRET_KEY` | Django secret key | `change-this-in-prod` |
| `DB_NAME` | PostgreSQL DB name | `edtech_db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `securepass` |
| `DB_HOST` | Database host | `localhost` |
| `RAZORPAY_KEY_ID` | Razorpay key ID | `rzp_test_xxx` |
| `RAZORPAY_KEY_SECRET` | Razorpay secret | `xxxxx` |
| `AWS_ACCESS_KEY_ID` | AWS key | `AKIAxxx` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret | `xxxxx` |
| `AWS_STORAGE_BUCKET_NAME` | S3 bucket name | `edtech-videos` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `EMAIL_HOST_USER` | Gmail address | `you@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail app password | `xxxx xxxx xxxx xxxx` |
| `SENTRY_DSN` | Sentry error tracking | `https://xxx@sentry.io/xxx` |

---

## 🔒 Security Features

- ✅ Token-based authentication (DRF)
- ✅ Razorpay signature verification (HMAC-SHA256)
- ✅ HTTPS enforcement in production
- ✅ CORS headers configured
- ✅ CSRF protection (Django built-in)
- ✅ XSS protection (Helmet headers)
- ✅ Rate limiting (django-ratelimit)
- ✅ Input validation (DRF serializers)
- ✅ PostgreSQL injection protection (ORM)
- ✅ WebSocket authentication (Channels middleware)
- ✅ S3 private ACL for videos (signed URLs)

---

## 🔧 Celery Tasks Schedule

| Task | Schedule | Description |
|---|---|---|
| `cleanup_pending_orders` | Daily midnight | Delete 24h+ old pending orders |
| `send_live_class_reminders` | Every 15 min | Email reminders 30 min before class |
| `generate_certificates` | Daily 2 AM | Certificate emails for completions |

---

## 📊 Django Admin Panel

Access at: **http://localhost:8000/admin/**

Manage:
- 👤 Users & Profiles
- 📚 Courses, Sections, Lessons
- 💳 Orders & Payments
- 🎥 Live Classes & Chat
- 🔔 Notifications
- 📁 Video uploads

---

## 🧪 Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test courses
python manage.py test payments
```

---

## 📈 Scaling Tips (5000+ users)

1. **Database**: Add `CONN_MAX_AGE = 600` (already set) + read replicas
2. **Caching**: Redis cache for course lists (5-min TTL)
3. **Celery**: Scale workers with `--concurrency=8`
4. **Static files**: CloudFront CDN
5. **Videos**: S3 + CloudFront for global delivery
6. **WebSockets**: Use Redis channel layer (already configured)
7. **Load balancing**: Run multiple Daphne instances behind Nginx

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

**Built with ❤️ using Django | PostgreSQL | Redis | Razorpay | AWS S3**
