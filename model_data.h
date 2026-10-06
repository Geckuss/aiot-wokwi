#pragma once

#include <stdint.h>

const int MODEL_INPUTS = 2;
const int MODEL_HIDDEN_UNITS = 8;
const int MODEL_OUTPUTS = 3;

const float NORMALIZATION_MEANS[MODEL_INPUTS] = {
  28.5166667f, 63.275f
};

const float NORMALIZATION_SCALES[MODEL_INPUTS] = {
  4.93623226f, 15.2952948f
};

const float HIDDEN_WEIGHT_SCALE = 0.0146570159f;
const int8_t HIDDEN_WEIGHTS[8][2] = {
  {-66, -87},
  {-94, -127},
  {-66, -58},
  {-123, -79},
  {-92, -111},
  {-22, -27},
  {-3, 2},
  {-33, -41},
};
const float HIDDEN_BIAS[8] = {
  -0.153700659f, -0.124707658f, 1.49865708f, 2.45717435f, -0.19996926f, -0.0317835936f, -0.012192751f, -0.0733005005f
};

const float OUTPUT_WEIGHT_SCALE = 0.0186040015f;
const int8_t OUTPUT_WEIGHTS[3][8] = {
  {66, 100, 13, -8, 90, 20, 4, 31},
  {-53, -63, 64, 127, -68, -15, 1, -27},
  {-15, -41, -83, -120, -19, -10, -2, -7},
};
const float OUTPUT_BIAS[3] = {
  -2.73027418f, -1.76219845f, 4.49247263f
};

const char* MODEL_LABELS[MODEL_OUTPUTS] = {
  "comfortable", "warning", "poor"
};
