#pragma once

#include <stdint.h>

const int MODEL_INPUTS = 2;
const int MODEL_HIDDEN_UNITS = 16;
const int MODEL_OUTPUTS = 3;

const float NORMALIZATION_MEANS[MODEL_INPUTS] = {
  22.0170787f, 45.9022472f
};

const float NORMALIZATION_SCALES[MODEL_INPUTS] = {
  4.25985973f, 22.4644537f
};

const float HIDDEN_WEIGHT_SCALE = 0.303456652f;
const int8_t HIDDEN_WEIGHTS[16][2] = {
  {1, -30},
  {2, -26},
  {12, -18},
  {-59, 0},
  {-23, 0},
  {-127, -1},
  {0, 42},
  {0, -17},
  {0, 80},
  {58, 0},
  {121, -5},
  {-1, 53},
  {-2, -61},
  {1, 44},
  {0, 0},
  {0, 0},
};
const float HIDDEN_BIAS[16] = {
  -9.15044087f, -9.50771821f, -3.48537074f, -12.6736929f, -8.07280984f, -45.0620503f, -14.1248057f, -6.29396372f, -26.6576984f, -12.6164551f, -41.4441067f, -18.0150846f, -13.4549963f, -7.96990623f, -0.00897785967f, -0.0148264019f
};

const float OUTPUT_WEIGHT_SCALE = 0.087895563f;
const int8_t OUTPUT_WEIGHTS[3][16] = {
  {-60, -20, 13, -113, -31, -20, -22, -13, -83, -108, -33, -89, -127, -93, 0, 1},
  {19, -54, 22, 56, 4, -58, -30, -31, -26, 55, -58, -2, 65, 33, 0, 0},
  {42, 72, -34, 56, 28, 79, 49, 45, 108, 54, 93, 91, 62, 60, -1, 0},
};
const float OUTPUT_BIAS[3] = {
  8.17488967f, 3.51561214f, -11.6905018f
};

const char* MODEL_LABELS[MODEL_OUTPUTS] = {
  "comfortable", "warning", "poor"
};
