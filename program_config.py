# Copyright 2020-2022 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice, this
# list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# Neither the name of the NXP Semiconductors nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
######################### Rails to probe #########################
By default, the program will loop over every power rail of the specified board sequentially.
If you want to read only a specific subset of rail(s), please modify the below variable, with 'rail_name'.
You can also specify power group.

Example for iMX8DXL EVK:
RAILS_TO_PROBE = ['5V0', '3V3_USB', 'VDD_SNVS1', 'GROUP_PLATFORM']
For rails' name please refer to board_name.py in directory board_configuration, structure mapping_power
"""
RAILS_TO_PROBE = ["all"]

# This offset is used to calculate the current limit for switching resistor to low_current shunt.
# By default, the value is defined to 10%, but the user can change it depending of the needs.
# The offset is deduce to the current limit. Higher is the offset, more restrictive is the switching.
# If current limit is 10mA with an offset of 10%, the average current should be < to 9mA to allow the shunt switching.
LOW_SWITCH_RESISTANCE_OFFSET = 10
