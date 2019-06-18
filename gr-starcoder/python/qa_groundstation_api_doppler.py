#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2019 Infostellar.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from groundstation_api_doppler import groundstation_api_doppler

from stellarstation.api.v1.groundstation import groundstation_pb2
import grpc
import grpc_testing

class qa_groundstation_api_doppler (gr_unittest.TestCase):

    def setUp (self):
        service_descriptors = [
            groundstation_pb2.DESCRIPTOR.services_by_name['GroundStationService']
        ]
        self.test_channel = grpc_testing.channel(service_descriptors, grpc_testing.strict_real_time())

        self.tb = gr.top_block()

    def tearDown(self):
        self.test_channel.close()
        self.test_channel = None
        self.tb = None

    def test_001_correct_response(self):
        gs_id = "1"
        plan_id = "2"

        groundstation_blk = groundstation_api_doppler("", "", "", gs_id, plan_id, 1, True, test_channel=self.test_channel)
        snk = blocks.message_debug()

        self.tb.msg_connect((groundstation_blk, 'doppler'), (snk, 'store'))

        self.tb.start()
        _, request, unary_unary_channel_rpc = self.test_channel.take_unary_unary(
            groundstation_pb2.DESCRIPTOR
                .services_by_name['GroundStationService']
                .methods_by_name['ListPlans']
        )
        unary_unary_channel_rpc.terminate(groundstation_pb2.ListPlansResponse(
            plan=[groundstation_pb2.Plan(plan_id="1"), groundstation_pb2.Plan(plan_id="2")]
        ), {}, grpc.StatusCode.OK, '')
        self.tb.stop()
        self.tb.wait()
        self.assertEqual(request.ground_station_id, gs_id)


if __name__ == '__main__':
    gr_unittest.run(qa_groundstation_api_doppler, "qa_groundstation_api_doppler.xml")
