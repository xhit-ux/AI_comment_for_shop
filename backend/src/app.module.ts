import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ScheduleModule } from '@nestjs/schedule';
import { TasksModule } from './tasks/tasks.module';
import { CommentsModule } from './comments/comments.module';
import { AnalysisModule } from './analysis/analysis.module';

@Module({
  imports: [
    // 数据库连接
    MongooseModule.forRoot('mongodb://localhost:27017/ecommerce_analysis', {
      // 生产环境建议使用环境变量
      // uri: process.env.MONGODB_URI,
    }),
    
    // 定时任务
    ScheduleModule.forRoot(),
    
    // 功能模块
    TasksModule,
    CommentsModule,
    AnalysisModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
