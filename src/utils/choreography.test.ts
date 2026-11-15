import test from 'node:test';
import assert from 'node:assert/strict';
import {
  SCENE_LAYERS,
  computePercentBounds,
  getTotalEntranceDurationMs,
  validateChoreographyOrder,
} from './choreography';

test('choreography guarantees dunes rise bottom-up before characters and trees', () => {
  const result = validateChoreographyOrder(SCENE_LAYERS);
  assert.equal(result.cloudsLoadWithSky, true);
  assert.equal(result.bottomDuneStartsFirst, true);
  assert.equal(result.dunesRiseBeforeSubjects, true);
});

test('computePercentBounds converts pixel rect to accurate percentages', () => {
  const bounds = computePercentBounds({ x: 100, y: 200, width: 200, height: 300 }, 1000, 2000);
  assert.equal(bounds.left, '10%');
  assert.equal(bounds.top, '10%');
  assert.equal(bounds.width, '20%');
  assert.equal(bounds.height, '15%');
});

test('total entrance duration finishes within a crisp ~3s window', () => {
  const total = getTotalEntranceDurationMs(SCENE_LAYERS);
  assert.ok(total >= 2200 && total <= 3200, `Expected 2200..3200ms, got ${total}`);
});
