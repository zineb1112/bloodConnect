# BloodConnect Database Documentation

## Overview

BloodConnect uses PostgreSQL as its primary database with a multi-schema architecture to separate concerns between the donor and hospital services.

## Database Architecture

### Schemas

1. **donor_schema** - Contains all donor-related data
2. **hospital_schema** - Contains all hospital-related data

### Connection Details

- **Host**: localhost
- **Port**: 5432
- **Database**: blood_db
- **Username**: blood_user
- **Password**: blood_pass (from environment variables)

## Schema Structure

### Donor Schema

#### Core Tables
- `donor_app_donor` - Main donor information
- `donor_app_donoruser` - Donor user accounts
- `auth_user` - Django authentication users
- `auth_group` - Django permission groups
- `auth_permission` - Django permissions
- `auth_user_groups` - User to group relationships
- `auth_user_user_permissions` - User to permission relationships
- `django_admin_log` - Admin activity log
- `django_content_type` - Content types for permissions
- `django_migrations` - Migration history
- `django_session` - User sessions

#### Relationships
- `donor_app_donoruser` references `auth_user` (One-to-One)
- `donor_app_donor` references `donor_app_donoruser` (One-to-One)

### Hospital Schema

#### Core Tables
- `hospital_app_hospital` - Hospital information
- `hospital_app_bloodrequest` - Blood requests from hospitals
- `hospital_app_campaign` - Blood donation campaigns
- `hospital_app_hospitaluser` - Hospital user accounts
- `auth_user` - Django authentication users
- `auth_group` - Django permission groups
- `auth_permission` - Django permissions
- `auth_user_groups` - User to group relationships
- `auth_user_user_permissions` - User to permission relationships
- `django_admin_log` - Admin activity log
- `django_content_type` - Content types for permissions
- `django_migrations` - Migration history
- `django_session` - User sessions

#### Relationships
- `hospital_app_hospitaluser` references `auth_user` (One-to-One)
- `hospital_app_hospital` references `hospital_app_hospitaluser` (One-to-One)
- `hospital_app_bloodrequest` references `hospital_app_hospital` (Foreign Key)
- `hospital_app_campaign` references `hospital_app_hospital` (Foreign Key)

## Access Methods

### 1. Django Admin Interface
Each service has its own Django admin interface:
- **Hospital Admin**: http://localhost:8000/admin
- **Donor Admin**: http://localhost:8001/admin

To create admin users:
```bash
# For Hospital service
docker exec -it hospital_service python manage.py createsuperuser

# For Donor service
docker exec -it donor_service python manage.py createsuperuser
```

### 2. Direct Database Access
Using psql or any PostgreSQL client:
```bash
psql -h localhost -p 5432 -U blood_user -d blood_db
```

### 3. Django Shell
Interactive Python shell with Django context:
```bash
# For Hospital service
docker exec -it hospital_service python manage.py shell

# For Donor service
docker exec -it donor_service python manage.py shell
```

## Migration Process

When adding new models or modifying existing ones:

1. Define your model in the appropriate app
2. Create migrations:
   ```bash
   # For Hospital service
   docker exec -it hospital_service python manage.py makemigrations
   
   # For Donor service
   docker exec -it donor_service python manage.py makemigrations
   ```
3. Apply migrations:
   ```bash
   # For Hospital service
   docker exec -it hospital_service python manage.py migrate
   
   # For Donor service
   docker exec -it donor_service python manage.py migrate
   ```

## Backup and Restore

### Backup
```bash
docker exec blood_db pg_dump -U blood_user blood_db > backup.sql
```

### Restore
```bash
docker exec -i blood_db psql -U blood_user blood_db < backup.sql
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure Docker containers are running
   ```bash
   docker-compose ps
   ```

2. **Permission Denied**: Check database credentials in .env file

3. **Migration Errors**: Check migration files and ensure they're consistent
   ```bash
   # Show migration status
   docker exec -it hospital_service python manage.py showmigrations
   docker exec -it donor_service python manage.py showmigrations
   ```

### Useful Queries

List all schemas:
```sql
SELECT schema_name FROM information_schema.schemata;
```

List all tables in a schema:
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'donor_schema';
SELECT table_name FROM information_schema.tables WHERE table_schema = 'hospital_schema';