# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : const.py
@Project  :
@Time     : 2025/3/28 17:30
@Author   : dylan
@Contact Email: cgq2012516@gmail.com
"""
import re

# IPv4 address (strict mode, excluding leading zeros)
IPV4_PATTERN = re.compile(r"^((25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}" r"(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$")

# IPv6 address pattern
IPV6_PATTERN = re.compile(
    r"("
    r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"  # 1:2:3:4:5:6:7:8
    r"([0-9a-fA-F]{1,4}:){1,7}:|"  # 1::                              1:2:3:4:5:6:7::
    r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"  # 1::8             1:2:3:4:5:6::8
    r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"  # 1::7:8         1:2:3:4:5::7:8
    r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"  # 1::6:7:8       1:2:3:4::6:7:8
    r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"  # 1::5:6:7:8     1:2:3::5:6:7:8
    r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"  # 1::4:5:6:7:8   1:2::4:5:6:7:8
    r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"  # 1::3:4:5:6:7:8  1::3:4:5:6:7:8
    r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"  # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8
    r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"  # fe80::7:8%eth0  fe80::7:8%1
    r"::(ffff(:0{1,4}){0,1}:){0,1}"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"  # ::255.255.255.255  ::ffff:255.255.255.255
    r"([0-9a-fA-F]{1,4}:){1,4}:"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"  # 1:2:3:4:5:6:255.255.255.255
    r")"
)

# Mainland China ID card (supports 15-digit old version and 18-digit new version)
ID_CARD_PATTERN = re.compile(
    r"^([1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx])$"  # 18 digits
    r"|^([1-9]\d{7}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3})$"  # 15 digits
)

# Mainland China mobile phone number (latest number segments)
PHONE_PATTERN = re.compile(
    r"^(?:\+?86)?"  # Optional international prefix
    r"1"  # First digit of the phone number
    r"(?:"  # Number segment grouping
    r"3[0-9]|"  # 130-139
    r"4[5-9]|"  # 145-149
    r"5[0-35-9]|"  # 150-153,155-159
    r"6[2567]|"  # 162,165,166,167
    r"7[0-8]|"  # 170-178
    r"8[0-9]|"  # 180-189
    r"9[0-35-9]"  # 190-193,195-199
    r")"  # End of number segment
    r"\d{8}$"  # Followed by 8 digits
)

# Bank card number (mainstream domestic bank formats)
BANK_CARD_PATTERN = re.compile(r"^([1-9]{1})(\d{15}|\d{18})$" r"|^(62\d{17})$")  # 16 or 19 digits  # UnionPay card

# Email address (RFC5322 standard)
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+"  # Local part
    r"@"
    r"(?=[a-zA-Z0-9-]{1,63}\.)"  # Domain pre-check
    r"([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"  # Subdomain
    r"[a-zA-Z]{2,63}$"  # Top-level domain
)

# International domain name (including Chinese domain names)
DOMAIN_PATTERN = re.compile(
    r"^([a-zA-Z0-9\u4e00-\u9fa5]"  # Support Chinese domain names
    r"(?:[a-zA-Z0-9\u4e00-\u9fa5-]{0,61}[a-zA-Z0-9\u4e00-\u9fa5])?\.)+"  # Subdomain
    r"[a-zA-Z\u4e00-\u9fa5]{2,63}$"  # Top-level domain
)

# URL pattern (simplified)
URL_PATTERN = re.compile(
    r"^(https?|ftp)://"  # Protocol
    r"([a-zA-Z0-9.-]+)"  # Domain name
    r"(:\d+)?"  # Optional port
    r"(\/[a-zA-Z0-9._-]*)*\/?$"  # Path
)

# Date pattern (YYYY-MM-DD)
DATE_PATTERN = re.compile(r"^\d{4}-" r"(0[1-9]|1[0-2])-" r"(0[1-9]|[12]\d|3[01])$")  # Year  # Month  # Day

# Time pattern (HH:MM:SS)
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):" r"[0-5]\d:" r"[0-5]\d$")  # Hours  # Minutes  # Seconds

# Hex color code pattern
HEX_COLOR_PATTERN = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")  # 6 or 3 hex digits

# US phone number pattern (123-456-7890)
US_PHONE_PATTERN = re.compile(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$")  # Area code and number

# Social Security Number (SSN) pattern (123-45-6789)
SSN_PATTERN = re.compile(r"^\d{3}-\d{2}-\d{4}$")  # SSN format

# Credit card number pattern (Visa, MasterCard, American Express, etc.)
CREDIT_CARD_PATTERN = re.compile(
    r"^(?:4[0-9]{12}(?:[0-9]{3})?"  # Visa
    r"|5[1-5][0-9]{14}"  # MasterCard
    r"|3[47][0-9]{13}"  # American Express
    r"|3(?:0[0-5]|[68][0-9])[0-9]{11}"  # Diners Club
    r"|6(?:011|5[0-9]{2})[0-9]{12}"  # Discover
    r"|(?:2131|1800|35\d{3})\d{11})$"  # JCB
)

# Password pattern
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])"  # At least one lowercase letter
    r"(?=.*[A-Z])"  # At least one uppercase letter
    r"(?=.*\W)"  # At least one special character
    r".{8,}$"  # At least 8 characters long
)

# Chinese postal code (6 digits)
POSTAL_CODE_PATTERN = re.compile(r"^\d{6}$")

# Chinese passport number (9 digits, starting with letter 'E' or 'G')
PASSPORT_PATTERN = re.compile(r"^[EG]\d{8}$")
