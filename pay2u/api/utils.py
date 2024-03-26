from typing import List, Dict


def query_min_price_sort(query: List[Dict[str, any]]) -> List[Dict[str, any]]:
    unique_subscriptions = []
    seen_services = set()
    for subscription in query:
        service_name = subscription["service_id__name"]
        if service_name not in seen_services:
            unique_subscriptions.append(subscription)
            seen_services.add(service_name)
        else:
            if subscription["price__min"] < unique_subscriptions[
                -1
            ]["price__min"]:
                unique_subscriptions[-1] = subscription
    return unique_subscriptions
