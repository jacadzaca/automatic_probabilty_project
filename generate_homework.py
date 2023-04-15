#!/usr/bin/env python3

X_RANGES = [
    (9.5,  10.5),
    (10.5, 11.5),
    (11.5, 12.5),
    (12.5, 13.5),
    (13.5, 14.5),
]

Y_RANGES = [
    (0.5, 1.0),
    (1.0, 1.5),
    (1.5, 2.0),
    (2.0, 2.5),
    (2.5, 3.0),
]


def average(xs):
    return sum(xs) / len(xs)


def create_observations_table(ns):
    if len(ns) < 6:
        raise ValueError('cannot create observations table from lists shorter than 6!')

    return [
        [  0,     0,     0,   ns[2], ns[2]],
        [  0,   ns[2], ns[3], ns[4], ns[3]],
        [ns[2], ns[3], ns[5], ns[3], ns[2]],
        [ns[3], ns[4], ns[3], ns[2],   0  ],
        [ns[2], ns[2],   0,     0,     0  ],
    ]


def sum_row(table, row_index):
    return sum(table[row_index])


def sum_column(table, column_index):
    column_sum = 0
    for row in table:
        column_sum += row[column_index]
    return column_sum


def dot_product(vector, other):
    return [i * j for i, j in zip(vector, other)]


def linear_regression_from_corelation_table(index):
    # leftmost part of the result table
    observation_table = create_observations_table(index)

    nk_column = [sum_row(observation_table, i) for i in range(len(observation_table))]
    ni_row = [sum_column(observation_table, i) for i in range(len(observation_table[0]))]
    if sum(ni_row) != sum(nk_column):
        raise ValueError('ni_row and nk_column dont sum to the same value!')

    # rightmsot part of the result table
    x_means = [average(x_range) for x_range in X_RANGES]
    y_means = [average(y_range) for y_range in Y_RANGES]

    y_mean_nk = dot_product(y_means, nk_column)

    y_mean_squared = dot_product(y_means, y_means)

    y_means_squared_nk = dot_product(y_mean_squared, nk_column)

    if len(x_means) != len(observation_table[0]):
        raise ValueError('observation_table and x_means must be of the same dimension')

    sums_x_mean_nik = [sum(dot_product(x_means, observation_table[i])) for i in range(len(observation_table))]

    sums_x_means_nik_times_y_mean = dot_product(sums_x_mean_nik, y_means)

    # bottom part of the result table
    x_mean_ni = dot_product(x_means, ni_row)

    x_means_squared = dot_product(x_means, x_means)

    x_means_squared_ni = dot_product(x_means_squared, ni_row)

    # calculation of coefficients
    x_mean = sum(dot_product(x_means, ni_row)) / sum(ni_row)
    y_mean = sum(dot_product(y_means, nk_column)) / sum(nk_column)

    x_variance = (sum(x_means_squared_ni) / sum(ni_row)) - x_mean**2
    y_variance = (sum(y_means_squared_nk) / sum(nk_column)) - y_mean**2


    nominator = (sum(sums_x_means_nik_times_y_mean) / sum(nk_column)) - (x_mean * y_mean)
    a = (nominator) / x_variance
    b = y_mean - a * x_mean
    a = round(a, 4)
    b = round(b, 4)

    a_prime = 1 / (nominator / y_variance)
    b_prime = y_mean - a_prime * x_mean
    a_prime = round(a_prime, 4)
    b_prime = round(b_prime, 4)


def main():
    linear_regression_from_corelation_table([0, 0, 1, 2, 3, 6])


if __name__ == '__main__':
    main()
