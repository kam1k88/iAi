-- PixelEncoder.lua (Добавляем данные для квестов, сумок и позиционирования)
local frame = CreateFrame("Frame", "PixelEncoderFrame", UIParent)
frame:SetSize(16, 1)
frame:SetPoint("TOPLEFT", UIParent, "TOPLEFT", 0, 0)
frame:SetFrameStrata("TOOLTIP")

local pixels = {}
for i = 1, 16 do
    local tex = frame:CreateTexture(nil, "OVERLAY")
    tex:SetSize(1, 1)
    tex:SetPoint("TOPLEFT", frame, "TOPLEFT", i - 1, 0)
    pixels[i] = tex
end

local function ToColor(val) return math.max(0, math.min(255, val or 0)) / 255 end

frame:SetScript("OnUpdate", function()
    -- 1: HP / Power
    pixels[1]:SetColorTexture(ToColor(UnitHealth("player")/UnitHealthMax("player")*100), ToColor(UnitPower("player")/UnitPowerMax("player")*100), 0, 1)
    -- 2: Target HP / Exists
    local hasT = UnitExists("target") and 100 or 0
    local tHP = hasT > 0 and (UnitHealth("target")/UnitHealthMax("target")*100) or 0
    pixels[2]:SetColorTexture(ToColor(tHP), ToColor(hasT), 0, 1)
    -- 3: Flags (Combat, Lootable, NeedRest)
    local f1 = (InCombatLockdown() and 1 or 0) + (CanLootUnit("target") and 2 or 0) + (UnitIsDead("player") and 4 or 0)
    pixels[3]:SetColorTexture(ToColor(f1), 0, 0, 1)
    -- 4: Free Bag Slots (Для контроля заполнении инвентаря)
    local freeSlots = 0
    for bag = 0, 4 do freeSlots = freeSlots + C_Container.GetContainerNumFreeSlots(bag) end
    pixels[4]:SetColorTexture(ToColor(freeSlots), 0, 0, 1)
    -- 5: Calibration Sync (Белый)
    pixels[5]:SetColorTexture(1, 1, 1, 1)
end)
