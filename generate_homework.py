#!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader

ENV = Environment(
        loader=FileSystemLoader(searchpath='.'),
        trim_blocks=True,
        lstrip_blocks=True
      )

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

    return (
        observation_table,
        nk_column,
        x_means,
        y_means,
        y_mean_nk,
        y_mean_squared,
        y_means_squared_nk,
        sums_x_mean_nik,
        sums_x_means_nik_times_y_mean,
        ni_row,
        x_mean_ni,
        x_means_squared,
        x_means_squared_ni,
        a,
        b,
        a_prime,
        b_prime
    )


def precision(f):
    if not isinstance(f, float) or f.is_integer():
        return 0
    return len(str(f).split('.')[-1])


def precision_sum(xs):
    biggset_precision = max(map(precision, xs))
    f_string = f'{{x:.{biggset_precision}f}}'
    return f_string.format(x=sum(xs))


def merge_results_in_table(
        observation_table,
        nk_column,
        x_means,
        y_means,
        y_mean_nk,
        y_mean_squared,
        y_means_squared_nk,
        sums_x_mean_nik,
        sums_x_means_nik_times_y_mean,
        ni_row,
        x_mean_ni,
        x_means_squared,
        x_means_squared_ni,
        a,
        b,
        a_prime,
        b_prime
    ):
    """generate a table like in the example"""
    column_order = [
        nk_column,
        y_mean_nk,
        y_mean_squared,
        y_means_squared_nk,
        sums_x_mean_nik,
        sums_x_means_nik_times_y_mean,
    ]
    previous_len = len(y_means)
    for column in column_order:
        if len(column) != previous_len:
            raise ValueError('columns are not of the same length!')
        previous_len = len(column)


    x_means += [None ] *len(y_means)
    result_table = [x_means]
    for i in range(len(y_means)):
        row = [y_means[i]] + observation_table[i]
        for column in column_order:
            biggset_precision = max(map(precision, column))
            if biggset_precision > 0:
                f_string = f'{{x:.{biggset_precision}f}}'
                row += [f_string.format(x=column[i])]
            else:
                row += [column[i]]
        result_table.append(row)


    ni_row += [precision_sum(ni_row), precision_sum(y_mean_nk), None, precision_sum(y_means_squared_nk), None, precision_sum(sums_x_means_nik_times_y_mean)]
    result_table.append(ni_row)
    x_mean_ni += [precision_sum(x_mean_ni)]
    result_table.append(x_mean_ni)
    result_table.append(x_means_squared)
    x_means_squared_ni.append(precision_sum(x_means_squared_ni))
    result_table.append(x_means_squared_ni)

    return result_table


def format_row(row):
    formatted_row = []

    for x in row:
        if x is None:
            x = ' '
        elif x == 0:
            x = '---'
        elif isinstance(x, float) and x.is_integer():
            x = int(x)

        formatted_row.append(str(x))

    return formatted_row


def main():
    result_table = merge_results_in_table(*linear_regression_from_corelation_table([0, 0, 1, 2, 3, 6]))
    result_table = [format_row(row) for row in result_table]

    latex = ENV \
            .get_template('homework_template.tex') \
            .render(
                x_means=result_table[0],
                yk_rows=[
                    result_table[1],
                    result_table[2],
                    result_table[3],
                    result_table[4],
                    result_table[5],
                ],
                nis=result_table[6],
                x_mean_nis=result_table[7],
                x_means_squared=result_table[8],
                x_mean_squared_nis=result_table[9],
            )
    print(latex)


if __name__ == '__main__':
    main()

