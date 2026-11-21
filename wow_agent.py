import time
import random
import mss
import numpy as np
import pyserial # Или вызовы вашего контроллера / Arduino USB

pyserial.FAILSAFE = True
import serial

class HardwareInput:
    def __init__(self, com_port="COM3"):
        # Открываем связь с физической платой Arduino
        self.ser = serial.Serial(com_port, 115200, timeout=1)
        time.sleep(2) # Пауза на инициализацию платы

    def press_key(self, key_char):
        cmd = f"PRESS:{key_char}\n"
        self.ser.write(cmd.encode('utf-8'))
        # Небольшая пауза между командами
        time.sleep(random.uniform(0.05, 0.12))

# Использование в боте:
# input_hw = HardwareInput("COM3")
# input_hw.press_key('f')

# --- 1. МОДУЛЬ ВОСПРИЯТИЯ (PERCEPTION) ---
class Perception:
    def __init__(self):
        self.sct = mss.mss()
        self.monitor = {"top": 0, "left": 0, "width": 16, "height": 1}

    def get_world_state(self):
        img = np.array(self.sct.grab(self.monitor)) # BGRA
        
        # Sync check (Pixel 5)
        if img[4] < 240:
            return None # Неверный кадр

        return {
            "player_hp": round((img[2] / 255.0) * 100),
            "player_power": round((img[1] / 255.0) * 100),
            "target_hp": round((img[1][2] / 255.0) * 100),
            "has_target": img[1] > 128,
            "in_combat": bool(int(img[2]) & 1),
            "is_dead": bool(int(img[2]) & 4),
            "free_slots": int(img[3][2]),
        }

# --- 2. МОДУЛЬ ИМИТАЦИИ ВВОДА (HUMANIZED INPUT) ---
class HumanInput:
    @staticmethod
    def press_key(key, hold_min=0.04, hold_max=0.09):
        """Нажатие клавиши со случайным удержанием"""
        pydirectinput.keyDown(key)
        time.sleep(random.uniform(hold_min, hold_max))
        pydirectinput.keyUp(key)

    @staticmethod
    def sleep_random(min_s=0.1, max_s=0.25):
        time.sleep(random.uniform(min_s, max_s))

# --- 3. ДВИЖОК СОСТОЯНИЙ (FINITE STATE MACHINE) ---
class BotFSM:
    def __init__(self):
        self.perception = Perception()
        self.input = HumanInput()
        self.state = "IDLE"
        self.last_action_time = time.time()

    def run_step(self):
        world = self.perception.get_world_state()
        if not world:
            print("\r[OFFLINE] Игра не сфокусирована или полоса перекрыта...", end="")
            time.sleep(0.5)
            return

        # Условия переключения состояний (Priority Hierarchy)
        if world["is_dead"]:
            self.state = "DEAD"
        elif world["in_combat"]:
            self.state = "COMBAT"
        elif world["player_hp"] < 35 or world["player_power"] < 20:
            self.state = "REST"
        elif world["free_slots"] < 2:
            self.state = "VENDOR_RUN"
        elif world["has_target"] and world["target_hp"] > 0:
            self.state = "APPROACH_AND_PULL"
        else:
            self.state = "SEARCH_TARGET"

        # Исполнение поведения в зависимости от состояния
        self.execute_state(world)

    def execute_state(self, world):
        print(f"\r[STATE: {self.state:15s}] HP: {world['player_hp']}% | MP: {world['player_power']}% | Target: {world['has_target']}", end="")

        if self.state == "COMBAT":
            # Выполнение боевой ротации (например, жмем 1, 2, 3)
            self.input.press_key('1') # Основной спелл / Fireball
            self.input.sleep_random(0.1, 0.2)
            
            if world["player_power"] > 30:
                self.input.press_key('2') # Доп. способность
            
        elif self.state == "REST":
            # Зажим клавиши питья/еды (например, '6')
            print("\n[ACTION] Низкий запас ресурсов. Пьем/Едим...")
            self.input.press_key('6')
            time.sleep(12) # Ждем восстановления

        elif self.state == "SEARCH_TARGET":
            # Таб-таргетинг и вращение камерой
            self.input.press_key('tab')
            self.input.sleep_random(0.3, 0.6)

        elif self.state == "APPROACH_AND_PULL":
            # Нажатие клавиши взаимодействия (Interact With Target - 'F')
            self.input.press_key('f')
            self.input.sleep_random(0.2, 0.4)

        elif self.state == "VENDOR_RUN":
            print("\n[ACTION] Сумки полны! Переход к логике продажи...")
            time.sleep(2)

        elif self.state == "DEAD":
            print("\n[ACTION] Персонаж погиб. Ожидание респауна...")
            time.sleep(5)

if __name__ == "__main__":
    bot = BotFSM()
    print("=== Автономный Агент WoW Forever Запущен ===")
    try:
        while True:
            bot.run_step()
            time.sleep(0.05) # 20 Hz цикл принятия решений
    except KeyboardInterrupt:
        print("\nБот остановлен.")
