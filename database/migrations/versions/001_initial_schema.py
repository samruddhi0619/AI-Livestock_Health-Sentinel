"""001_initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-04 15:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # 2. Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('fullname', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('FARMER', 'VETERINARIAN', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('district', sa.String(length=50), nullable=True),
        sa.Column('taluka', sa.String(length=50), nullable=True),
        sa.Column('village', sa.String(length=50), nullable=True),
        sa.Column('license_number', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_role', 'users', ['role'])

    # 3. Animals Table
    op.create_table(
        'animals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('animal_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('qr_code_identifier', sa.String(length=100), nullable=False, unique=True),
        sa.Column('species', sa.String(length=30), nullable=False, default='Cattle'),
        sa.Column('breed', sa.String(length=50), nullable=False),
        sa.Column('age', sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column('gender', sa.Enum('Female', 'Male', name='animalgender'), nullable=False),
        sa.Column('owner_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('health_status', sa.Enum('HEALTHY', 'SUSPECTED', 'CONFIRMED_SICK', 'UNDER_TREATMENT', 'RECOVERED', 'DECEASED', name='animalhealthstatus'), nullable=False, default='HEALTHY'),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column('village', sa.String(length=50), nullable=True),
        sa.Column('taluka', sa.String(length=50), nullable=True),
        sa.Column('district', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_animals_tag_id', 'animals', ['animal_id'])
    op.create_index('idx_animals_qr_code', 'animals', ['qr_code_identifier'])
    op.create_index('idx_animals_owner', 'animals', ['owner_id'])
    op.create_index('idx_animals_health_status', 'animals', ['health_status'])

    # 4. Animal Health Records Table
    op.create_table(
        'animal_health_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('animal_id', sa.String(length=36), sa.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recorded_by_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('body_temperature_c', sa.Numeric(precision=4, scale=1), nullable=False),
        sa.Column('heart_rate_bpm', sa.Integer(), nullable=True),
        sa.Column('respiratory_rate_bpm', sa.Integer(), nullable=True),
        sa.Column('appetite_score', sa.Numeric(precision=2, scale=1), nullable=False, default=1.0),
        sa.Column('milk_yield_liters', sa.Numeric(precision=4, scale=1), nullable=False, default=0.0),
        sa.Column('activity_score', sa.Numeric(precision=2, scale=1), nullable=False, default=1.0),
        sa.Column('rumination_hours', sa.Numeric(precision=3, scale=1), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_health_records_animal', 'animal_health_records', ['animal_id'])
    op.create_index('idx_health_records_recorded_at', 'animal_health_records', ['recorded_at'])

    # 5. Vaccination Records Table
    op.create_table(
        'vaccination_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('animal_id', sa.String(length=36), sa.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vaccine_name', sa.String(length=100), nullable=False),
        sa.Column('batch_number', sa.String(length=50), nullable=True),
        sa.Column('administered_date', sa.Date(), nullable=False),
        sa.Column('next_due_date', sa.Date(), nullable=False),
        sa.Column('administered_by_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.Enum('ADMINISTERED', 'SCHEDULED', 'OVERDUE', 'EXEMPTED', name='vaccinationstatus'), nullable=False, default='ADMINISTERED'),
        sa.Column('certificate_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_vaccinations_animal', 'vaccination_records', ['animal_id'])
    op.create_index('idx_vaccinations_due_date', 'vaccination_records', ['next_due_date'])

    # 6. Symptom Reports Table
    op.create_table(
        'symptom_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('health_record_id', sa.String(length=36), sa.ForeignKey('animal_health_records.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('reported_by_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('symptoms', sa.JSON(), nullable=False),
        sa.Column('onset_days_ago', sa.Integer(), nullable=False, default=1),
        sa.Column('severity_level', sa.Enum('MILD', 'MODERATE', 'SEVERE', name='symptomseverity'), nullable=False, default='MILD'),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('reported_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 7. Image Reports Table
    op.create_table(
        'image_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('health_record_id', sa.String(length=36), sa.ForeignKey('animal_health_records.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('uploaded_by_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('image_hash_sha256', sa.String(length=64), nullable=True),
        sa.Column('body_part', sa.String(length=50), nullable=False, default='Full Body'),
        sa.Column('quality_check_passed', sa.Boolean(), nullable=False, default=True),
        sa.Column('blur_laplacian_var', sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column('brightness_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False)
    )

    # 8. AI Predictions Table (Strict separation: Probabilistic, NEVER definitive diagnosis)
    op.create_table(
        'ai_predictions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('health_record_id', sa.String(length=36), sa.ForeignKey('animal_health_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('symptom_report_id', sa.String(length=36), sa.ForeignKey('symptom_reports.id', ondelete='SET NULL'), nullable=True),
        sa.Column('image_report_id', sa.String(length=36), sa.ForeignKey('image_reports.id', ondelete='SET NULL'), nullable=True),
        sa.Column('prediction_type', sa.Enum('IMAGE_VISION', 'SYMPTOM_TABULAR', 'ENVIRONMENTAL_RISK', 'MULTIMODAL_FUSION', name='predictiontype'), nullable=False),
        sa.Column('predicted_condition', sa.String(length=100), nullable=False),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('risk_level', sa.Enum('LOW', 'MODERATE', 'HIGH', name='risktier'), nullable=False),
        sa.Column('risk_score', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('all_class_probabilities', sa.JSON(), nullable=False),
        sa.Column('contributing_symptoms', sa.JSON(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('is_veterinary_diagnosis', sa.Boolean(), nullable=False, default=False),
        sa.Column('disclaimer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_ai_predictions_record', 'ai_predictions', ['health_record_id'])
    op.create_index('idx_ai_predictions_risk', 'ai_predictions', ['risk_level', 'risk_score'])

    # 9. Disease Clusters Table
    op.create_table(
        'disease_clusters',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('cluster_code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('disease_name', sa.String(length=100), nullable=False),
        sa.Column('center_latitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('center_longitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('radius_km', sa.Numeric(precision=6, scale=2), nullable=False),
        sa.Column('case_count', sa.Integer(), nullable=False, default=1),
        sa.Column('severity', sa.Enum('WATCH', 'WARNING', 'EMERGENCY', name='clusterseverity'), nullable=False, default='WARNING'),
        sa.Column('status', sa.Enum('ACTIVE', 'CONTAINED', 'DISSOLVED', name='clusterstatus'), nullable=False, default='ACTIVE'),
        sa.Column('district', sa.String(length=50), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_case_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_clusters_code', 'disease_clusters', ['cluster_code'])

    # 10. Disease Reports Table
    op.create_table(
        'disease_reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('animal_id', sa.String(length=36), sa.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False),
        sa.Column('health_record_id', sa.String(length=36), sa.ForeignKey('animal_health_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('ai_prediction_id', sa.String(length=36), sa.ForeignKey('ai_predictions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reported_disease', sa.String(length=100), nullable=False),
        sa.Column('reporting_source', sa.Enum('FARMER_SELF_REPORT', 'AI_SENTINEL_SCREENING', 'VETERINARIAN_FIELD_VISIT', 'COMMUNITY_PARAVET', name='reportingsource'), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=False),
        sa.Column('status', sa.Enum('PENDING_REVIEW', 'VERIFIED_POSITIVE', 'REJECTED_FALSE_ALARM', 'RESOLVED_RECOVERED', name='diseasereportstatus'), nullable=False, default='PENDING_REVIEW'),
        sa.Column('is_quarantine_required', sa.Boolean(), nullable=False, default=False),
        sa.Column('cluster_id', sa.String(length=36), sa.ForeignKey('disease_clusters.id', ondelete='SET NULL'), nullable=True),
        sa.Column('reported_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_disease_reports_animal', 'disease_reports', ['animal_id'])
    op.create_index('idx_disease_reports_status', 'disease_reports', ['status'])
    op.create_index('idx_disease_reports_disease', 'disease_reports', ['reported_disease'])

    # 11. Alerts Table
    op.create_table(
        'alerts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('recipient_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('alert_type', sa.Enum('OUTBREAK_EARLY_WARNING', 'CLUSTER_PROXIMITY_ALERT', 'VACCINATION_OVERDUE', 'CASE_TRIAGE_REQUIRED', 'HIGH_RISK_SYMPTOM', name='alerttype'), nullable=False),
        sa.Column('severity', sa.Enum('INFO', 'MODERATE', 'CRITICAL', name='alertseverity'), nullable=False, default='INFO'),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('related_cluster_id', sa.String(length=36), sa.ForeignKey('disease_clusters.id', ondelete='SET NULL'), nullable=True),
        sa.Column('related_animal_id', sa.String(length=36), sa.ForeignKey('animals.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_alerts_recipient', 'alerts', ['recipient_id'])
    op.create_index('idx_alerts_created_at', 'alerts', ['created_at'])

    # 12. Veterinarian Reviews Table (Strict separation: Independent Human Clinical Adjudication)
    op.create_table(
        'veterinarian_reviews',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('disease_report_id', sa.String(length=36), sa.ForeignKey('disease_reports.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('veterinarian_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('review_decision', sa.Enum('CONFIRMED_POSITIVE', 'RULED_OUT_NEGATIVE', 'INCONCLUSIVE_RETEST', 'DIFFERENTIAL_DIAGNOSIS', name='reviewdecision'), nullable=False),
        sa.Column('clinical_diagnosis', sa.String(length=100), nullable=False),
        sa.Column('laboratory_test_type', sa.String(length=100), nullable=True),
        sa.Column('laboratory_result', sa.String(length=50), nullable=True),
        sa.Column('treatment_plan', sa.Text(), nullable=True),
        sa.Column('prescribed_medications', sa.Text(), nullable=True),
        sa.Column('quarantine_order_issued', sa.Boolean(), nullable=False, default=False),
        sa.Column('quarantine_duration_days', sa.Integer(), nullable=False, default=0),
        sa.Column('revisit_date', sa.Date(), nullable=True),
        sa.Column('clinical_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False)
    )
    op.create_index('idx_vet_reviews_report', 'veterinarian_reviews', ['disease_report_id'])
    op.create_index('idx_vet_reviews_vet', 'veterinarian_reviews', ['veterinarian_id'])

def downgrade() -> None:
    op.drop_table('veterinarian_reviews')
    op.drop_table('alerts')
    op.drop_table('disease_reports')
    op.drop_table('disease_clusters')
    op.drop_table('ai_predictions')
    op.drop_table('image_reports')
    op.drop_table('symptom_reports')
    op.drop_table('vaccination_records')
    op.drop_table('animal_health_records')
    op.drop_table('animals')
    op.drop_table('users')
