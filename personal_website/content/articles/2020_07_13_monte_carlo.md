Title: Monte Carlo Localization in robotics
Date: 2020-07-13 10:00

A succesful example of classical robot localization in low dimensional spaces is theParticle Filter. The term Particle Filter was proposed by Del Moral (1996), followed by the Sequential Monte Carlo (SMC) naming in Liu and Chen (1998). The theory compromises ofa broad family of sequential Monte Carlo algorithms that approximate inference in partially observable Markov chains and is well described in Pitt and Shephard (1999) and Thrun(2002). For robotics, the algorithm input data is usually gathered from sensors mounted onthe mobile platform. The Particle Filters have solved two problems, that were previously unsolvable for other localization algorithms:

- Global localization problem - Borenstein et al. (1996),
- Kidnapped robot problem - Engelson and McDermott (1992).

While the Particle Filter algorithm is often used in modern robotic localization (usually complimentary), it is not without fault. Two major issues about the algorithm limitations are shown:

- While performing well in low dimensional spaces, it has poor performance in highdimensional spaces. The particles need to cover a vast space and their number increases exponentially making it computationally heavy.
- The algorithm isn’t suited for simultaneous localization and mapping (SLAM) problems. Without an initial map of the area, Monte Carlo Localization cannot be run successfully.

The issues were partially solved by so-called Rao-Blackwellized particle filters, seeMurphy (1999), Doucet et al. (2001), Montemerlo et al. (2002a) and Montemerlo et al.(2002b). These particle filters lead to solutions for SLAM problems that are more efficient than the Extended Kalman Filter methods. These particle filters require time

$$
O(MlogN)
$$

instead of

$$
O(N_2)
$$

, where $M$ is the number of particles. Thrun (2002) suggests that empirical evidence shows that $M$ can be a constant in situations with bounded uncertainty - which includes all SLAM problems that can be solved via Extended Kalman Filters. Moreover experimental results suggest that particle filters provide a better solution to the data association problem than currently available with the EKF.

Monte Carlo Localization, also called the recursive Bayes Filter, takes sensor data and estimates the posterior intelligent agent position. Bayes Filtering help in estimation of thestatexin a dynamic system (partially observable Markov chains). The main assumption of Bayes Filters is that the current state of the robot in a Markov environment is conditionally independent to the past and future states. The idea behind Bayes Filtering is to estimate aprobability density over the state space based on the gathered data - this is usually called the Belief. The initial Belief describes the knowledge about the initial state of the system. When the initial state is unknown, the initial Belief is initialized by an uniform distribution over the state space (for mobile robotics, this refers to the global localization problem).

The implementation of the recursive Belief equation in a continuous space, is not asimple matter according to Thrun et al. (2000b), when computational efficiency is involved. The idea shared by particle algorithms (including MCL), is to represent the belief by a set of $m$ weighted samples with according to the belief.

The recursive update of the robot localization is realized as enumerated below (the MCL pseudocode). The sampling routine is repeated $m$ times, producing a set of $m$ weighted samples. Lastly the importance factors are normalized, so that they sum up to 1, defining a discrete probability distribution.

```
def particle_filter(X, a, o):
    X <- new empty array
    for i in range(0, m):
        random(x) <- from X according to w_1, ..., w_m
        random(x') ~ p(x' | a, x)
        X'.append(<x', w'>)
    Normalize importance factors w in X'
    return X'
```
