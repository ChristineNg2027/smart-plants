#include <stdio.h>
#include "driver/gpio.h"
#include "esp_adc/adc_oneshot.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

//internal LED
#define LED_PIN GPIO_NUM_42
#define MOISTURE_INPUT_GPIO 20

//poll every 15 mintues
#define POLLING_PERIOD 15 * 60 * 1000 

TaskHandle_t monitorTaskHandle = NULL;

struct Callibration {
    char name[20];
    int min;
    int max;
};

typedef struct {
    adc_oneshot_unit_handle_t adc_handle;
    adc_channel_t channel;
    struct Callibration *cal;
    int iterations;
} MonitorTaskCtx;

static MonitorTaskCtx monitor_ctx;

struct Callibration moistureCal = {"sensor 1", 400, 2500};

int measureMoisture(adc_oneshot_unit_handle_t adc_handle, adc_channel_t channel, struct Callibration *cal){
    int rawData;
    adc_oneshot_read(adc_handle, channel, &rawData);
    int computedData = 100.0f * (cal->max - rawData) / (cal->max - cal->min);
    return computedData;

}

void monitorMoistureTask(void *pvParameters) {
    while(1) {
        MonitorTaskCtx *ctx = (MonitorTaskCtx *)pvParameters;
        int total = 0; 
        for(int i = 0; i < ctx->iterations; i++) {
            total += measureMoisture(ctx->adc_handle, ctx->channel, ctx->cal);
            vTaskDelay(100);
        }

        printf("Average Moisture: %d\n", total / ctx->iterations);

        vTaskDelay(POLLING_PERIOD);
    }
}

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
    monitor_ctx = (MonitorTaskCtx){ .adc_handle = adc_handle, .channel = channel, .cal = &moistureCal, .iterations = 10 };


    vTaskDelay(1000);

    xTaskCreatePinnedToCore(monitorMoistureTask, "Moisture Monitor", 4096, &monitor_ctx, 1, &monitorTaskHandle, 1);

    while (1) {
        gpio_set_level(LED_PIN, state);
        state ^= 1;
        vTaskDelay(500);
    }
    
}
