import os
import subprocess
import json
import settings
from pydantic import BaseModel
from typing import Optional
from settings import logger

class PowerAutomateData(BaseModel):
    full_name_ua:           str
    full_name_en:           str
    front_or_back_office:   str
    phone:         Optional[str] = None
    title_ua:      Optional[str] = None
    title_en:      Optional[str] = None
    department:    Optional[str] = None
    manager:       Optional[str] = None
    action_status: Optional[str] = None


def prepare_user_info(data: PowerAutomateData):
    full_name_ua_str = data.full_name_ua
    full_name_en_str = data.full_name_en
    
    full_name_ua = full_name_ua_str.split()
    full_name_en = full_name_en_str.split()

    last_name_ua  = full_name_ua[0] if len(full_name_ua) > 0 else ""
    first_name_ua = full_name_ua[1] if len(full_name_ua) > 1 else ""

    first_name_en = full_name_en[0] if len(full_name_en) > 0 else ""
    last_name_en  = full_name_en[1] if len(full_name_en) > 1 else ""

    title_en = data.title_en
    title_ua = data.title_ua
    title    = f"{title_en} | {title_ua}"

    email = f"{first_name_en}.{last_name_en}@tsum.com.ua"
    manager_name = data.manager
    department = data.department
    phone = data.phone


    ps_script = os.path.join(os.getcwd(), "create_user\\create_user_ad.ps1")
    args = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        f"[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; & '{ps_script}' "
        f"-FirstNameUA \"{first_name_ua}\" "
        f"-LastNameUA \"{last_name_ua}\" "
        f"-FirstNameEN \"{first_name_en}\" "
        f"-LastNameEN \"{last_name_en}\" "
        f"-UserUPNlogon \"{email}\" "
        f"-Office \"{settings.OFFICE}\" "
        f"-Email \"{email}\" "
        f"-WebPage \"{settings.WEB_PAGE}\" "
        f"-Phone \"{phone}\" "
        f"-Title \"{title}\" "
        f"-DepartmentName \"{department}\" "
        f"-Company \"{settings.COMPANY}\" "
        f"-ManagerName \"{manager_name}\" "
        f"-Description \"{title}\""
    ]

    logger.info(f"\nВиклик PowerShell з аргументами:\n{' '.join(args)}\n")
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')


    if result.returncode == 0:
        logger.success(f"Обліковий запис для {first_name_ua} {last_name_ua} успішно створено в AD.")
    
    raw_output = result.stdout.strip()
    if raw_output:
        try:
            # 1. Перетворюємо вивід PowerShell у Python-словник
            ad_data = json.loads(raw_output)
            
            # 2. Робимо копію виключно для безпечного логування
            log_data = ad_data.copy()
            if "UserPassword" in log_data:
                log_data["UserPassword"] = "***"
            
            # 3. Записуємо в лог безпечну копію
            logger.info(f"PowerShell вивід: {json.dumps(log_data, ensure_ascii=False)}")
        except json.JSONDecodeError:
            # Резервний варіант, якщо PowerShell несподівано вивів не JSON текст
            logger.info(f"PowerShell вивід (не JSON): {raw_output}")
    else:
        # Якщо сталась помилка в PowerShell
        logger.error(f"Помилка створення облікового запису для {first_name_ua} {last_name_ua}")
        logger.error(f"Деталі помилки: {result.stderr.strip()}")

    return result
