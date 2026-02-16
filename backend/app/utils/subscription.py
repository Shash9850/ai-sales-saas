from datetime import datetime

def is_store_active(store):
    if not store.is_active:
        return False

    if store.subscription_end and store.subscription_end < datetime.utcnow():
        return False

    return True
