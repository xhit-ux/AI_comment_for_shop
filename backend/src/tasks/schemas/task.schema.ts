import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document, Types } from 'mongoose';

export type TaskDocument = Task & Document;

export enum TaskStatus {
  PENDING = 'pending',
  COLLECTING = 'collecting',
  CLEANING = 'cleaning',
  ANALYZING = 'analyzing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum PlatformType {
  JD = 'jd',
  TAOBAO = 'taobao',
  TMALL = 'tmall',
  PDD = 'pdd',
}

@Schema({ timestamps: true })
export class Task {
  @Prop({ required: true })
  name: string;

  @Prop()
  description: string;

  @Prop({ required: true, enum: PlatformType })
  platform: PlatformType;

  @Prop({ required: true })
  productUrl: string;

  @Prop()
  productId: string;

  @Prop({ required: true, enum: TaskStatus, default: TaskStatus.PENDING })
  status: TaskStatus;

  @Prop({ type: Object })
  config: {
    maxComments: number;
    includeFollowUp: boolean;
    includeImageComments: boolean;
    includeVideoComments: boolean;
    timeRange?: {
      start: Date;
      end: Date;
    };
  };

  @Prop({ default: 0 })
  commentCount: number;

  @Prop({ default: 0 })
  analyzedCount: number;

  @Prop()
  errorMessage: string;

  @Prop()
  startedAt: Date;

  @Prop()
  completedAt: Date;

  @Prop({ type: Types.ObjectId, ref: 'Product' })
  product: Types.ObjectId;
}

export const TaskSchema = SchemaFactory.createForClass(Task);
