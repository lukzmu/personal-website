Title: Potential fields in path planning
Date: 2020-09-15 10:00

While Bug algorithms work well (without constructing a configuration space) in two-dimensional spaces, they are limited to that. To move into a multidimensional, non-Euclidean space, potential functions were introduced. We can describe the potential function as a differentiable real-valued function $U: \mathbb{R}^m \to \mathbb{R}$, which value can be seen as energy. Therefore the gradient of the potential can be seen as force, and its vector can be described as follows:

$$
\bigtriangledown U(q) = DU(q)^T = [\frac{\partial U}{\partial q_1}(q), ..., \frac{\partial U}{\partial q_m}(q)]^T
$$

which points in the direction where locally maximally increases $U$. This gradient is used to define a vector field, assigning vectors to each point in the map.

An example output of a potential function is shown in the image below. The potential function treats the robot as a particle moving through the gradient vector field. Such gradient can be treated as a force field, that acts on a positively charged robot and moves it into the direction of a negative charge, that is the goal $q_{goal}$. Each obstacle is also positively charged, so it repulses the robot away from itself. The combination of those two techniques: attraction and repulsion, navigates the robot from its starting point $q_{start}$ to the goal $q_{goal}$.

The potential function, is calculated by the sum of all effects that attract the robot and repel it. With describing the attractive potential field for a point $q$ as $U_{att}(q)$ and the repulsive potential field as $U_{rep}(q)$, we get the following equation:

$$
U(q) = U_{att}(q) + U_{rep}(q)
$$

The attraction from the potential field $U_{att}$ should monotonically increase with the distance from the goal. Using the conic potential, we can measure the distance to the goal as $U(q) = \zeta d(q, q_{goal})$, where $\zeta$ is a scaling parameter. As the attractive gradient vector points away from the goal with a magnitude of $\zeta$ to all points (excluding the goal), giving a negated gradient as described:

$$
\bigtriangledown U(q) = \frac{\zeta}{d(q, q_{goal})}(q - q_{goal})
$$

This imposes some “chattering” problems due to the discontinuity in the attactive gradient at the origin. To tackle that problem, a potential function that is continuously differentiable is needed. With a simple potential function, that grows quadratically with the distance to the goal, we can get:

$$
U_{att}(q) = \frac{1}{2}\zeta d_2(q, q_{goal})
$$

and with the gradient:

$$
\bigtriangledown U_{att}(q) = \bigtriangledown \left(\frac{1}{2}\zeta d^2(q, q_{goal})\right) = \frac{1}{2}\zeta \bigtriangledown d^2(q, q_{goal}) = \zeta(q - q_{goal})
$$

A problem we encounter is that while $\bigtriangledown U_{att}(q)$ converges linealy to zero as it approaches the goal, it grows significantly when the robot moves away from the goal $q_{goal}$. When the start and goal are away by a significant distance, the produced velocity is too large. A good solution is to combine the quadratic and conic potentials, in order to produce the following switching behavior:

- If the robot is very distant from $q_{goal}$ use the conic potential,
- If the robot is close to the $q_{goal}$ use quadratic potential.

We can define this behavior in the following way:

$$
U_{att}(q) = \begin{cases} \frac{1}{2} \zeta d^2(q, q_{goal}), & d(q, q_{goal}) \leq d_{goal}^*,\\ d_{goal}^* \zeta d(q, q_{goal}) - \frac{1}{2} \zeta (d_{goal}^*)^2, & d(q, q_{goal}) \gt d_{goal}^*.\\ \end{cases}
$$

and with the gradient:

$$
\bigtriangledown U_{att}(q) = \begin{cases} \zeta (q - q_{goal}), & d(q, q_{goal}) \leq d_{goal}^*,\\ \frac{d_{goal}^* \zeta(q - q_{goal})}{d(q, q_{goal})}, & d(q, q_{goal}) \gt d_{goal}^*.\\ \end{cases}
$$

On the other hand, the repulsive potential of a field keeps the robot away from environment obstacles. The closer the robot is to an obstacle, the higher the applied repulsive force should be - this value should monotonically decrease with the distance from the obstacle. This behavior, for the closest obstacle $D(q)$ is usually defined as:

$$
U_{rep}(q) = \begin{cases} \frac{1}{2} \eta (\frac{1}{D(q)} - \frac{1}{Q^*})^2, & D(q) \leq Q^*, \\ 0, & D(q) \gt Q^*.\\ \end{cases}
$$

and with the gradient:

$$
\bigtriangledown U_{rep}(q) = \begin{cases} \eta (\frac{1}{Q^*} - \frac{1}{D(q)}) \frac{1}{D^2(q)} \bigtriangledown D(q), & D(q) \leq Q^*,\\ 0, & D(q) \gt Q^*.\\ \end{cases}
$$

where $\eta$ is the gain of the gradient, and is determined empirically. Similarly to the attraction gradient, this is prone to error due to oscillations between obstacles. To avoid this, the repulsive potential function should be defined in terms of dinstances to individual obstacles (as opposed to the closest obstacle), where $d_i(q)$ is the distance to obstacle $QO_i$ for all points $c$ in the environment:

$$
d_i(q) = \underset{c \in QO_i}{min} d(q, c)
$$

giving each obstacle its own potential function:

$$
U_{rep_i} = \begin{cases} \frac{1}{2} \eta ( \frac{1}{d_i(q)} - \frac{1}{Q_i^*})^2, & \text{if } d_i(q) \leq Q_i^*, \\ 0, & \text{if } d_i(q) \gt Q_i^*.\\ \end{cases}
$$

Potential fields can be treated as landscapes, where the robot moves from high to low valued states, minimizing the value of the local potential function. The idea is to navigate from the robot starting point $q_{start}$ to the local minima, preferably at the goal position. Such path is created using a method called gradient descent.

One of the crucial problems of gradient descent techniques with robotic path planning is the local minima problem. It is generally guaranteed, that the gradient descent will converge to a minimum field, but without guarantee that this field will be a global minimum (our goal point $q_{goal}$). This can happen when the obstacles are placed in a certain way - as an example horseshoe shaped objects or obstacles placed close to each other (counteracting the goal attraction), repulsing the robot away. A proposed solution to this problem is the **Randomized Path Planner (RPP)**. RPP worked as described, until it reached a local minima point. Then it initiated a series of random walks, that resulted in escaping the local minimum and allowed following the negative gradient again to reach the goal.

Another interesting solution to the local minimum problem is the **Wave-Front Planner**. The downside of this algorithm is that it can only be implemented in spaces represented as grids. The planner is initialized with a grid that depicts free space as 0 and obstacles as 1, as well as start and goal coordinations (goal marked as 2). The algorithm iterates around the neighbours increasing the assigned number to the grid field. As an example:

- The goal is labeled with a value of 2,
- All zero-valued neighbours of the goal field are labeled with a value of 3,
- All zero-valued neighbours of fields with value of 3 are labeled with a value of 4,
- Continue the above behavior, increasing the number.
- This behavior continues until the wave front reaches the start point cell.

Once the wave front field is created, the planner begins the behavior of path creation. The path is created using the previously described gradient descent technique. Due to the fact, how the wave front field was constructed, there will always be a smaller number in each of the steps, which guarantees the path creation to reach the global minimum, which is the $q_{goal}$ of our algorithm. Although the examples are presented in two-dimensions, this algorithm can be applied without issues to multi-dimensional problems.
