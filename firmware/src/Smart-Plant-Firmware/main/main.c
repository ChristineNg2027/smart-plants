#include <stdio.h>
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

//internal LED
#define LED_PIN GPIO_NUM_42
#define MOISTURE_INPUT_GPIO 20

struct Callibration {
    char name[20];
    int min;
    int max;
};

struct Callibration moistureCal = {"sensor 1", 800, 2000};

void app_main(void)
{
    gpio_config_t led_config = {
        .pin_bit_mask = (1ULL << LED_PIN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&led_config);

    adc_unit_t unit;
    adc_channel_t channel;
    ESP_ERROR_CHECK(adc_oneshot_io_to_channel(MOISTURE_INPUT_GPIO, &unit, &channel));

    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t unit_cfg = {
        .unit_id = unit,
        .ulp_mode = ADC_ULP_MODE_DISABLE,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit_cfg, &adc_handle));

    adc_oneshot_chan_cfg_t chan_cfg = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc_handle, channel, &chan_cfg));

    int state = 0;
    int raw = 0;

    vTaskDelay(1000);

    while (1) {
        gpio_set_level(LED_PIN, state);
        state ^= 1;
        vTaskDelay(raw / 10);
        
        printf("Moisture= %d\n", monitorMoisture(adc_handle, channel, &moistureCal));
    }
    
}

int monitorMoisture(adc_oneshot_unit_handle_t adc_handle, adc_channel_t channel, struct Callibration *cal){
    int rawData;
    adc_oneshot_read(adc_handle, channel, &rawData);
    int computedData = (rawData - cal -> min / (4095.0 - (cal -> min + cal -> max))) * 100;
    return computedData;

}
