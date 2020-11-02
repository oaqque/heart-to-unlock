/*
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the Institute nor the names of its contributors
 *    may be used to endorse or promote products derived from this software
 *    without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE INSTITUTE AND CONTRIBUTORS ``AS IS'' AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE INSTITUTE OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 *
 * This file is part of the Contiki operating system.
 *
 */

#include "contiki.h"
#include "contiki-lib.h"
#include "contiki-net.h"
#include "sys/ctimer.h"	
#include "board-peripherals.h"

#include <string.h>
#include <stdio.h>
#include <stdint.h>

#define DEBUG DEBUG_PRINT
#include "net/ip/uip-debug.h"

#define UIP_IP_BUF   ((struct uip_ip_hdr *)&uip_buf[UIP_LLH_LEN])

#define MAX_PAYLOAD_LEN 120
#define SAMPLE_RATE 500
#define NUM_SAMPLES_SEND 20

static struct uip_udp_conn *server_conn;
static struct	ctimer sensor_timer;				
static int value;
static int countSamples;
static int collected_samples[NUM_SAMPLES_SEND];

PROCESS(udp_server_process, "UDP server process");
AUTOSTART_PROCESSES(&resolv_process,&udp_server_process);
/*---------------------------------------------------------------------------*/
static void sensor_callback(void	*ptr)		{	
  value = mpu_9250_sensor.value(MPU_9250_SENSOR_TYPE_GYRO_X);		
  // printf("Value=%d.%02d\n\r", value/100, value%100);
  int idx = countSamples % NUM_SAMPLES_SEND;
  collected_samples[idx] = value;
  countSamples++;
  if (countSamples <= 600) { 
    if (countSamples % NUM_SAMPLES_SEND == 0) {
      PRINTF("SENDING DATA...\n");
      uip_udp_packet_sendto(server_conn, collected_samples, sizeof(collected_samples), &server_conn->ripaddr, UIP_HTONS(3000));
      memset(collected_samples, 0, NUM_SAMPLES_SEND);
    }
    ctimer_set(&sensor_timer, CLOCK_SECOND / SAMPLE_RATE, sensor_callback, NULL); // Callback timer for lux sensor
  } else {
    SENSORS_DEACTIVATE(mpu_9250_sensor);
    PRINTF("All samples sent\n");
  }
}		
/*---------------------------------------------------------------------------*/
static void
tcpip_handler(void)
{
  if(uip_newdata()) {
    PRINTF("SensorTag Received Start Signal from \n");
    PRINT6ADDR(&UIP_IP_BUF->srcipaddr);
    PRINTF("\n");
    uip_ipaddr_copy(&server_conn->ripaddr, &UIP_IP_BUF->srcipaddr);
    PRINTF("Starting collection of data...\n");
  }
}
/*---------------------------------------------------------------------------*/
static void
print_local_addresses(void)
{
  int i;
  uint8_t state;

  PRINTF("Server IPv6 addresses: ");
  for(i = 0; i < UIP_DS6_ADDR_NB; i++) {
    state = uip_ds6_if.addr_list[i].state;
    if(uip_ds6_if.addr_list[i].isused &&
       (state == ADDR_TENTATIVE || state == ADDR_PREFERRED)) {
      PRINT6ADDR(&uip_ds6_if.addr_list[i].ipaddr);
      PRINTF("\n\r");
    }
  }
}
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(udp_server_process, ev, data)
{
#if UIP_CONF_ROUTER
  uip_ipaddr_t ipaddr;
#endif /* UIP_CONF_ROUTER */

  PROCESS_BEGIN();
  PRINTF("UDP server started\n\r");

#if RESOLV_CONF_SUPPORTS_MDNS
  resolv_set_hostname("contiki-udp-server");
#endif

#if UIP_CONF_ROUTER
  uip_ip6addr(&ipaddr, 0xaaaa, 0, 0, 0, 0, 0, 0, 0);
  uip_ds6_set_addr_iid(&ipaddr, &uip_lladdr);
  uip_ds6_addr_add(&ipaddr, 0, ADDR_AUTOCONF);
#endif /* UIP_CONF_ROUTER */

  print_local_addresses();
  //Create UDP socket and bind to port 3000
  server_conn = udp_new(NULL, UIP_HTONS(0), NULL);
  udp_bind(server_conn, UIP_HTONS(3001));
  char buf[MAX_PAYLOAD_LEN];
  while(1) {
    PROCESS_YIELD();

	  //Wait for tcipip event to occur
    if(ev == tcpip_event) {
      tcpip_handler();
      SENSORS_ACTIVATE(mpu_9250_sensor);
    } else if (ev == sensors_event && data == &mpu_9250_sensor) {
      ctimer_set(&sensor_timer, CLOCK_SECOND / SAMPLE_RATE, sensor_callback, NULL);	//Callback timer for lux sensor
    }
  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/	