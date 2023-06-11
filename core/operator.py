from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from app.tasks import (
    update_day_gainers,
    update_day_losers,
    update_top_crypto,
    update_global_indicator,
    update_indian_indicator
)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)

    @scheduler.scheduled_job('interval', seconds=60, name='update_gainer_losser_crypto')
    def update_gainer_losser_crypto():
        update_day_gainers()
        update_day_losers()
        update_top_crypto()
    
    @scheduler.scheduled_job('interval', seconds=30, name='update_global')
    def update_global():
        update_global_indicator()

    @scheduler.scheduled_job('interval', seconds=10, name='update_indian')
    def update_indian():
        update_indian_indicator()

    scheduler.start()
