#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class DynamicController(Node):

    def __init__(self):
        super().__init__('dynamic_controller')

        # Each obstacle has an independent state machine.
        self.obstacles = [
            {
                'name': 'obstacle_1',
                'topic': '/dynamic_obstacle_1/cmd_vel',
                'axis': 'x',
                'speed': 0.3,
                'leg_duration': 6.0,
                'dwell_duration': 2.0,
                'state': 'moving',
                'direction': 1.0,
            },
            {
                'name': 'obstacle_2',
                'topic': '/dynamic_obstacle_2/cmd_vel',
                'axis': 'y',
                'speed': 0.25,
                'leg_duration': 5.0,
                'dwell_duration': 1.5,
                'state': 'moving',
                'direction': 1.0,
            },
            {
                'name': 'obstacle_3',
                'topic': '/dynamic_obstacle_3/cmd_vel',
                'axis': 'x',
                'speed': 0.2,
                'leg_duration': 7.0,
                'dwell_duration': 1.0,
                'state': 'moving',
                'direction': 1.0,
            },
        ]

        now = self.get_clock().now()

        for obstacle in self.obstacles:
            obstacle['pub'] = self.create_publisher(
                Twist,
                obstacle['topic'],
                10
            )

            obstacle['state_start_time'] = now

        # 20 Hz control loop
        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info(
            'Dynamic controller started for 3 obstacles'
        )

        for obstacle in self.obstacles:
            self.get_logger().info(
                f"{obstacle['name']}: "
                f"axis={obstacle['axis']}, "
                f"speed={obstacle['speed']} m/s, "
                f"topic={obstacle['topic']}"
            )

    def control_loop(self):

        now = self.get_clock().now()

        for obstacle in self.obstacles:

            elapsed = (
                now - obstacle['state_start_time']
            ).nanoseconds / 1e9

            msg = Twist()

            if obstacle['state'] == 'moving':

                velocity = (
                    obstacle['speed']
                    * obstacle['direction']
                )

                if obstacle['axis'] == 'x':
                    msg.linear.x = velocity

                elif obstacle['axis'] == 'y':
                    msg.linear.y = velocity

                if elapsed >= obstacle['leg_duration']:
                    obstacle['state'] = 'dwelling'
                    obstacle['state_start_time'] = now

            else:  # dwelling

                # Twist defaults to all zeros.

                if elapsed >= obstacle['dwell_duration']:

                    obstacle['direction'] *= -1.0
                    obstacle['state'] = 'moving'
                    obstacle['state_start_time'] = now

            obstacle['pub'].publish(msg)

    def stop_all_obstacles(self):

        stop_msg = Twist()

        for obstacle in self.obstacles:
            obstacle['pub'].publish(stop_msg)


def main(args=None):

    rclpy.init(args=args)

    node = DynamicController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.stop_all_obstacles()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()