#include <windows.h>
#include <iostream>
#include <vector>

// Типы функций Lua API внутри движка WoW
typedef int(__cdecl* Lua_CFunction)(uintptr_t L);
typedef void(__cdecl* tLua_RegisterFunction)(const char* name, Lua_CFunction func);

// Глобальные адреса и оригинальные байты
uintptr_t g_WorldBaseAddress = 0;
uintptr_t g_IsProtectedFunctionAddr = 0; // Офсет функции проверки защиты
BYTE g_OriginalBytes[2] = { 0 };

// Вспомогательная функция для патчинга памяти
bool PatchMemory(uintptr_t address, const BYTE* patchData, size_t size) {
    DWORD oldProtect;
    // Разрешаем запись в страницу памяти кода
    if (!VirtualProtect((LPVOID)address, size, PAGE_EXECUTE_READWRITE, &oldProtect)) {
        return false;
    }

    // Сохраняем оригинальные байты для возможности отката
    memcpy(g_OriginalBytes, (void*)address, size);
    // Записываем патч (например, mov al, 1; ret -> 0xB0, 0x01, 0xC3)
    memcpy((void*)address, patchData, size);

    // Восстанавливаем исходные права защиты страницы
    VirtualProtect((LPVOID)address, size, oldProtect, &oldProtect);
    return true;
}

// Кастомная C-функция, экспортируемая в Lua-среду игры
int Custom_ClickToMove(uintptr_t L) {
    // В реальном коде здесь считываются X, Y, Z из стека Lua 
    // и вызывается внутренняя C++ функция CGPlayer_C::ClickToMove
    std::cout << "[Unlocker] Вызвана команда движения ClickToMove!" << std::endl;
    return 0; // Количество возвращаемых значений в Lua
}

// Главная логика разблокировки
void ApplyUnlocker() {
    g_WorldBaseAddress = (uintptr_t)GetModuleHandle(NULL);

    // 1. Пример патчинга проверки защищенных функций (Protected Lua Functions)
    // Патч: mov al, 1 (0xB0, 0x01) -> ret (0xC3)
    BYTE patchBytes[] = { 0xB0, 0x01, 0xC3 };
    
    // Адрес функции меняется при каждом патче игры (offset)
    g_IsProtectedFunctionAddr = g_WorldBaseAddress + 0x1A2B3C4; // Пример офсета для патча 16001

    if (PatchMemory(g_IsProtectedFunctionAddr, patchBytes, sizeof(patchBytes))) {
        std::cout << "[SUCCESS] Защита Lua API успешно снята (Protected API Unlocked)!" << std::endl;
    } else {
        std::cout << "[ERROR] Не удалось применить патч памяти." << std::endl;
    }

    // 2. Снятие флагов InCombatLockdown (Unwrap / Automation)
    // Разработчики анлокеров сбрасывают флаги блокировки боя прямо в структуре состояния Lua
}

// Точка входа в DLL (Вызывается при инъекции в process wow.exe)
DWORD WINAPI MainThread(LPVOID lpParam) {
    // Создаем консоль для отладки вывода
    AllocConsole();
    freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);

    std::cout << "=== WoW Forever Memory Unlocker Initialized ===" << std::endl;

    ApplyUnlocker();

    while (!(GetAsyncKeyState(VK_END) & 1)) {
        Sleep(100);
    }

    // Восстановление памяти перед выгрузкой DLL
    PatchMemory(g_IsProtectedFunctionAddr, g_OriginalBytes, sizeof(g_OriginalBytes));
    FreeConsole();
    FreeLibraryAndExitThread((HMODULE)lpParam, 0);
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    if (ul_reason_for_call == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hModule);
        CreateThread(NULL, 0, MainThread, hModule, 0, NULL);
    }
    return TRUE;
}