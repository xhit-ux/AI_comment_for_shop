import { Injectable, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { Task, TaskDocument, TaskStatus } from './schemas/task.schema';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';

@Injectable()
export class TasksService {
  constructor(
    @InjectModel(Task.name) private taskModel: Model<TaskDocument>,
  ) {}

  async create(createTaskDto: CreateTaskDto): Promise<Task> {
    const taskConfig = {
      maxComments: createTaskDto.maxComments,
      includeFollowUp: createTaskDto.includeFollowUp,
      includeImageComments: createTaskDto.includeImageComments,
      includeVideoComments: createTaskDto.includeVideoComments,
      timeRange: createTaskDto.timeRange,
    };

    const createdTask = new this.taskModel({
      ...createTaskDto,
      config: taskConfig,
      status: TaskStatus.PENDING,
    });

    return createdTask.save();
  }

  async findAll(params: {
    page: number;
    limit: number;
    status?: string;
    platform?: string;
  }): Promise<{ tasks: Task[]; total: number; page: number; pages: number }> {
    const { page, limit, status, platform } = params;
    const skip = (page - 1) * limit;

    const filter: any = {};
    if (status) filter.status = status;
    if (platform) filter.platform = platform;

    const [tasks, total] = await Promise.all([
      this.taskModel
        .find(filter)
        .sort({ createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .exec(),
      this.taskModel.countDocuments(filter),
    ]);

    return {
      tasks,
      total,
      page,
      pages: Math.ceil(total / limit),
    };
  }

  async findOne(id: string): Promise<Task> {
    const task = await this.taskModel.findById(id).exec();
    if (!task) {
      throw new NotFoundException(`Task with ID ${id} not found`);
    }
    return task;
  }

  async update(id: string, updateTaskDto: UpdateTaskDto): Promise<Task> {
    const existingTask = await this.taskModel
      .findByIdAndUpdate(id, updateTaskDto, { new: true })
      .exec();

    if (!existingTask) {
      throw new NotFoundException(`Task with ID ${id} not found`);
    }

    return existingTask;
  }

  async remove(id: string): Promise<void> {
    const result = await this.taskModel.findByIdAndDelete(id).exec();
    if (!result) {
      throw new NotFoundException(`Task with ID ${id} not found`);
    }
  }

  async startTask(id: string): Promise<Task> {
    const task = await this.taskModel.findByIdAndUpdate(
      id,
      {
        status: TaskStatus.COLLECTING,
        startedAt: new Date(),
        errorMessage: null,
      },
      { new: true },
    );

    if (!task) {
      throw new NotFoundException(`Task with ID ${id} not found`);
    }

    // TODO: 触发Python爬虫服务
    // this.triggerCrawler(task);

    return task;
  }

  async retryTask(id: string): Promise<Task> {
    const task = await this.taskModel.findByIdAndUpdate(
      id,
      {
        status: TaskStatus.PENDING,
        errorMessage: null,
      },
      { new: true },
    );

    if (!task) {
      throw new NotFoundException(`Task with ID ${id} not found`);
    }

    return task;
  }

  async getTaskStats(id: string): Promise<any> {
    const task = await this.findOne(id);
    
    // TODO: 从评论集合中获取统计信息
    const stats = {
      totalComments: task.commentCount,
      analyzedComments: task.analyzedCount,
      progress: task.commentCount > 0 ? (task.analyzedCount / task.commentCount) * 100 : 0,
      sentimentDistribution: {
        positive: 0,
        negative: 0,
        neutral: 0,
      },
      // 其他统计信息...
    };

    return stats;
  }

  async updateTaskProgress(id: string, progress: {
    commentCount?: number;
    analyzedCount?: number;
    status?: TaskStatus;
    errorMessage?: string;
  }): Promise<Task> {
    const updateData: any = { ...progress };
    
    if (progress.status === TaskStatus.COMPLETED) {
      updateData.completedAt = new Date();
    }

    const task = await this.taskModel.findByIdAndUpdate(id, updateData, { new: true }).exec();
    
    if (!task) {
      throw new NotFoundException(`Task with ID ${id} not found`);
    }

    return task;
  }

  // 私有方法：触发爬虫服务
  private async triggerCrawler(task: Task): Promise<void> {
    // TODO: 调用Python爬虫服务的HTTP接口
    // 这里可以集成消息队列或直接HTTP调用
    console.log(`Triggering crawler for task ${task._id}`);
  }
}
