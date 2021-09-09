------------------------------------------------------------
-- блок объявления --
------------------------------------------------------------
--ПЕРЕФЕРИЯ
-- инициализируем светодиоды
local ledNumber = 29
local leds = Ledbar.new(ledNumber)

--  инициализируем Uart интерфейс
local uartNum = 4 -- номер Uart интерфейса (USART4)
local baudRate = 9600 -- скорость передачи данных
local dataBits = 8
local stopBits = 1
local parity = Uart.PARITY_NONE
local uart = Uart.new(uartNum, baudRate, parity, stopBits) --  создание протокола обмена

-- ПЕРЕМЕННЫЕ
-- флаги
local IS_FLIGHT = false
local POINT_DECELERATION = false


local function changeColor(red, green, blue)
   for i=0, ledNumber - 1, 1 do
       leds:set(i, red, green, blue)
   end
end


------------------------------------------------------------
-- блок приема сообщений --
------------------------------------------------------------
local message_position = {} -- очередь выполнения команд полета
function getData() -- функция приёма пакета данных
    if uart:bytesToRead() ~= 0 then
        message = uart:read(16) -- их точно 16?
		
		type_mes, x, y, z, f =  string.unpack( ">c2 f f f c1", message)
		
		--if type_mes == "CC" then
		--	changeColor(x, y, z)
		--end
		
    end
end


-- Функция обработки событий
-- и флаги

function callback(event)
	-- Когда коптер поднялся на высоту взлета Flight_com_takeoffAlt, переходим к полету по точкам
    if(event == Ev.TAKEOFF_COMPLETE) then
    end
    
	-- Когда коптер достиг текущей точки, переходим к следующей
    if(event == Ev.POINT_DECELERATION) then
		POINT_DECELERATION = true
    end
    
	-- Когда коптер приземлился, выключаем светодиоды
    if (event == Ev.COPTER_LANDED) then
    end
end

changeColor(0, 0, 0)
local time_timer = 0.2
timer = Timer.new(time_timer, function() getData() end)
timer:start()
