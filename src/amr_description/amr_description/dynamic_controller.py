#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class DynamicController(Node):
    """
    Deterministic back-and-forth (Option A) controller for a single
    planar-move-plugin obstacle. Publishes a fixed velocity for
    LEG_DURATION seconds, then zero velocity for DWELL_DURATION
    seconds, then reverses. Repeats indefinitely.
    """

    def __init__(self):
        super().__init__('dynamic_controller')

        # --- Fixed, deterministic parameters (same every run) ---
        self.cmd_topic = '/dynamic_obstacle_1/cmd_vel'
        self.speed = 0.3          # m/s
        self.leg_duration = 6.0   # seconds of motion per leg
        self.dwell_duration = 2.0 # seconds of zero-velocity pause

        self.pub = self.create_publisher(Twist, self.cmd_topic, 10)

        # State machine: 'moving' or 'dwelling'
        self.state = 'moving'
        self.direction = 1.0  # +1 = +x, -1 = -x
        self.state_start_time = self.get_clock().now()

        # 20 Hz control loop
        self.timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info(
            f'DynamicObstacleController started on {self.cmd_topic} '
            f'(speed={self.speed} m/s, leg={self.leg_duration}s, '
            f'dwell={self.dwell_duration}s)'
        )

    def control_loop(self):
        now = self.get_clock().now()
        elapsed = (now - self.state_start_time).nanoseconds / 1e9

        msg = Twist()

        if self.state == 'moving':
            msg.linear.x = self.speed * self.direction
            if elapsed >= self.leg_duration:
                self.state = 'dwelling'
                self.state_start_time = now
        else:  # dwelling
            msg.linear.x = 0.0
            if elapsed >= self.dwell_duration:
                self.direction *= -1.0
                self.state = 'moving'
                self.state_start_time = now

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = DynamicController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the obstacle cleanly on shutdown
        stop_msg = Twist()
        node.pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()