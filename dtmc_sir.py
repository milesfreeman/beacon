
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def Prob_dist(time, population):
	t = time
	d_dt = 0.01
	beta = d_dt
	b = d_dt / 4
	gamma = d_dt / 4
	N = population

	Trans = np.zeros(((N+1) , (N+1)))
	Z = np.zeros(((time+1), (N+1)))
	v = np.array(np.arange(0,N+1,1.0))
	Z[0][2] = 1.0
	bt = np.array([N - x for x in v]) / N
	bt = np.array(map(lambda x,y: x * y * beta, v, bt))
	dt = (b + gamma) * v

	for i in range(1,N) :
		Trans[i][i] = 1 - bt[i] - dt[i]
		Trans[i][i+1] = dt[i + 1]
		Trans[i+1][i] = bt[i]

	Trans[0][0] = 1
	Trans[0][1] = dt[1]
	Trans[N][N] = 1 - dt[N]

	for j in range(t) :
		y = np.matmul(Trans, Z[j])
		Z[j + 1] = np.transpose(y)

	i_s = range(N+1)
	t_s = range(t+1)

	hf = plt.figure()
	ha = hf.add_subplot(111, projection='3d')
	X, Y = np.meshgrid(i_s, t_s)
	ha.plot_wireframe(X, Y, Z)
	ha.set_xlabel('# infected')
	ha.set_ylabel('Time')
	ha.set_zlabel('Probability')
	hf.suptitle('P[I(t)] for N = %d' % N)
	plt.show()
	return Trans

def simulate(prob, iterations, interval):
	times = np.array(range(interval + 1))
	colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
	for i in range(iterations):
		infecteds = np.zeros(len(times))
		i_t = 2
		for t in range(interval + 1):
			if i_t:
				p_ij = np.array([prob[i_t][i_t -1], prob[i_t][i_t], prob[i_t][i_t + 1]])
				i_t += np.random.choice(range(-1,2), p = (p_ij / np.sum(p_ij)))
				infecteds[t] = i_t
			else:
				break
		plt.plot(times, infecteds, colors[i])
		plt.xlabel('Time')
		plt.ylabel('Number Infected')
	def deterministic(I_t):
		a = ((0.25 / 100) * (100 - I_t)) - 0.5
		return np.exp(a * I_t) + 2
	f = np.vectorize(deterministic)
	x = np.array(np.arange(0, interval + 0.1, 0.1))
	y = f(x)
	plt.plot(x,y, 'k')
	plt.show()


def main():
	P = Prob_dist(2000, 100)
	simulate(P, 4, 2000)

main()
