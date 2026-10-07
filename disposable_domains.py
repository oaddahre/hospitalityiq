"""Known disposable/throwaway email domains, blocked at registration.

This is a small, hand-maintained list of the most common temporary-inbox
services — not an exhaustive database (there are commercial APIs with
tens of thousands of entries for that). Add to it as new ones show up in
registration attempts; keep entries lowercase, one per set literal below.
"""

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com",
    "guerrillamail.com",
    "guerrillamail.net",
    "guerrillamail.org",
    "guerrillamail.info",
    "guerrillamail.biz",
    "guerrillamailblock.com",
    "sharklasers.com",
    "grr.la",
    "10minutemail.com",
    "10minutemail.net",
    "20minutemail.com",
    "temp-mail.org",
    "tempmail.com",
    "tempmail.net",
    "temp-mail.io",
    "tempail.com",
    "throwawaymail.com",
    "trashmail.com",
    "trashmail.net",
    "yopmail.com",
    "yopmail.net",
    "yopmail.fr",
    "maildrop.cc",
    "mintemail.com",
    "fakeinbox.com",
    "getnada.com",
    "mohmal.com",
    "dispostable.com",
    "spamgourmet.com",
    "mailnesia.com",
    "mailcatch.com",
    "moakt.com",
    "emailondeck.com",
    "33mail.com",
    "mytemp.email",
    "tempinbox.com",
    "inboxbear.com",
    "discard.email",
    "discardmail.com",
}


def is_disposable_email(email: str) -> bool:
    domain = (email or "").rsplit("@", 1)[-1].strip().lower()
    return domain in DISPOSABLE_EMAIL_DOMAINS
