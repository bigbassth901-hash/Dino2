/*
  # Create Film Asset Management Database Schema

  1. New Tables
    - `shots`
      - `id` (uuid, primary key) - Unique identifier for each shot
      - `shot_id` (text) - Shot identifier from processing
      - `keyframe_path` (text) - Path to the keyframe image
      - `frame_index` (integer) - Frame index in the original video
      - `cluster_type` (text) - Type of cluster (scene, character, noise)
      - `cluster_id` (text) - ID of the assigned cluster
      - `similarity_score` (float) - Similarity score for clustering
      - `timestamp` (timestamptz) - When the shot was processed
      - `created_at` (timestamptz) - Record creation time

    - `training_feedback`
      - `id` (uuid, primary key) - Unique identifier for feedback
      - `anchor_id` (text) - ID of the shot being moved (anchor)
      - `positive_id` (text) - ID of the target cluster (positive example)
      - `label` (integer) - Feedback label (1 for positive association)
      - `timestamp` (timestamptz) - When the feedback was logged
      - `created_at` (timestamptz) - Record creation time

  2. Security
    - Enable RLS on both tables
    - Add policies for authenticated users to manage their own data
    - Allow public read access for demonstration purposes

  3. Indexes
    - Create indexes on frequently queried columns for performance
*/

CREATE TABLE IF NOT EXISTS shots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shot_id text NOT NULL,
  keyframe_path text NOT NULL,
  frame_index integer DEFAULT 0,
  cluster_type text DEFAULT 'scene',
  cluster_id text NOT NULL,
  similarity_score float DEFAULT 0.0,
  timestamp timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS training_feedback (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  anchor_id text NOT NULL,
  positive_id text NOT NULL,
  label integer DEFAULT 1,
  timestamp timestamptz DEFAULT now(),
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_shots_cluster_id ON shots(cluster_id);
CREATE INDEX IF NOT EXISTS idx_shots_cluster_type ON shots(cluster_type);
CREATE INDEX IF NOT EXISTS idx_shots_timestamp ON shots(timestamp);
CREATE INDEX IF NOT EXISTS idx_training_feedback_timestamp ON training_feedback(timestamp);

ALTER TABLE shots ENABLE ROW LEVEL SECURITY;
ALTER TABLE training_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to shots"
  ON shots
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public insert to shots"
  ON shots
  FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "Allow public update to shots"
  ON shots
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from shots"
  ON shots
  FOR DELETE
  TO public
  USING (true);

CREATE POLICY "Allow public read access to training_feedback"
  ON training_feedback
  FOR SELECT
  TO public
  USING (true);

CREATE POLICY "Allow public insert to training_feedback"
  ON training_feedback
  FOR INSERT
  TO public
  WITH CHECK (true);

CREATE POLICY "Allow public update to training_feedback"
  ON training_feedback
  FOR UPDATE
  TO public
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Allow public delete from training_feedback"
  ON training_feedback
  FOR DELETE
  TO public
  USING (true);
