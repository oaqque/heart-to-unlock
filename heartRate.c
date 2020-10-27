/**
 * \file
 *         A TCP socket echo server. Listens and replies on port 8080
 * \author
 *         mds
 */

#include "contiki.h"
#include "contiki-net.h"
#include "sys/cc.h"
#include "dev/leds.h"
#include "sys/etimer.h"
#include "buzzer.h"
#include "dev/serial-line.h"
#include "dev/cc26xx-uart.h"
#include "sys/ctimer.h"
#include "ieee-addr.h"

#include "board-peripherals.h"
// #include "ti-lib.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "utils.h"

#define SERVER_PORT 8080
#define DEFAULT_BUZZ_FREQ 1000

static struct tcp_socket socket;

#define INPUTBUFSIZE 400
static uint8_t inputbuf[INPUTBUFSIZE];

#define OUTPUTBUFSIZE 400
static uint8_t outputbuf[OUTPUTBUFSIZE];

static char myBuff[INPUTBUFSIZE];

#define PAR_LEN 30

#define START_STRING "Starting transmission\n\r"
#define END_STRING "Ending transmission\n\r"

PROCESS(tcp_server_process, "TCP echo process");
PROCESS(gyro_thread, "IMU process thread");
AUTOSTART_PROCESSES(&tcp_server_process, &gyro_thread);

// static uint8_t get_received;
// static int bytes_to_send;

static struct ctimer imu_timer;

int counter = 0;
int frequency = 10; //Hz
int num_samples = 100;

int getSampleFlag = 0;


// Function definitions
void process_key(char c);
void imu_init();
void imu_callback(void *);
static bool processRequest(int bytes, char* data);

/*---------------------------------------------------------------------------*/
//Input data handler
static int input(struct tcp_socket *s, void *ptr, const uint8_t *inputptr, int inputdatalen) {

  printf("input %d bytes '%s'\n\r", inputdatalen, inputptr);


	if (!processRequest(inputdatalen, inputptr)) {
		tcp_socket_send_str(&socket, inputptr);	//Reflect data
		tcp_socket_send_str(&socket, "\n\r");	
	}

	//Clear buffer
	memset(inputptr, 0, inputdatalen);
    return 0; // all data consumed 
}

/*---------------------------------------------------------------------------*/
//Event handler
static void event(struct tcp_socket *s, void *ptr, tcp_socket_event_t ev) {
  printf("event %d\n", ev);
}

/*---------------------------------------------------------------------------*/

void closeSocket() {
	tcp_socket_close(&socket);
}

void returnError() {
	tcp_socket_send_str(&socket, "Error!\n\rExpected: GET /acceleration/{num_samples}/{frequency}\n\r");
	closeSocket();
}

static bool processRequest(int bytes, char* data) {
	data[bytes-1]='\0';
	char par1[PAR_LEN] = {0};
	char par2[PAR_LEN] = {0};
	char par3[PAR_LEN] = {0};
	bool err = true;
	if (startsWith("GET", data)) {
		// Expecting Path: /acceleration/{num_samples}/{frequency}
		int numParams = parseGetRequest(data, bytes, PAR_LEN, par1, par2, par3);
		if (numParams == 3) {
			if (strcmp(par1, "acceleration") == 0) {
				if (myAtoi(par2, &num_samples) && myAtoi(par3, &frequency)) {
					tcp_socket_send_str(&socket, START_STRING);
					imu_init(NULL);
					err = false;
				}
			}
		}
	}
	if (err) returnError(data);
	return !err;
}

/*---------------------------------------------------------------------------*/
//TCP Server process
PROCESS_THREAD(tcp_server_process, ev, data) {

  	PROCESS_BEGIN();

	//Register TCP socket
  	tcp_socket_register(&socket, NULL,
               inputbuf, sizeof(inputbuf),
               outputbuf, sizeof(outputbuf),
               input, event);
  	tcp_socket_listen(&socket, SERVER_PORT);

	while(1) {
	
		//Wait for event to occur
		PROCESS_PAUSE();
	}
	PROCESS_END();
}

/*---------------------------------------------------------------------------*/
//Sensors thread
int convertData(int x) {
	return x;
	// return (int)(x * 1.0) / (65536 / 500);
}

void send_return(int x, int y, int z) {
    int len = sprintf(myBuff, "{%d, %d, %d}\n\r", convertData(x), convertData(y), convertData(z));
	tcp_socket_send_str(&socket, myBuff);
	memset(myBuff, 0, len);
}
void imu_init() {
	getSampleFlag = 1;
    mpu_9250_sensor.configure(SENSORS_ACTIVE, MPU_9250_SENSOR_TYPE_ACC);
    SENSORS_ACTIVATE(mpu_9250_sensor);
}

void imu_callback(void *ptr) {
    if (counter >= num_samples) {
        counter = 0;
		if (num_samples != 0) {
			tcp_socket_send_str(&socket, END_STRING);
		}
		closeSocket();
		SENSORS_DEACTIVATE(mpu_9250_sensor);
        return;
    }
	getSampleFlag = 1;
    counter++;
}

PROCESS_THREAD(gyro_thread, ev, data) {
    int val_x;
    int val_y;
    int val_z;

    PROCESS_BEGIN();

    while(1) {
        PROCESS_YIELD();

        if (ev == sensors_event && getSampleFlag == 1) {
            if (data == &mpu_9250_sensor) {
                val_x = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_ACC_X);
                val_y = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_ACC_Y);
                val_z = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_ACC_Z);
                // SENSORS_DEACTIVATE(mpu_9250_sensor);
				getSampleFlag = 0;
                ctimer_set(&imu_timer, CLOCK_SECOND/frequency, imu_callback, NULL);
                send_return(val_x, val_y, val_z);
            }
        }
    }

    PROCESS_END();
}
