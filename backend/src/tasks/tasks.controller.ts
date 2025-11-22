import { 
  Controller, 
  Get, 
  Post, 
  Body, 
  Patch, 
  Param, 
  Delete, 
  Query 
} from '@nestjs/common';
import { TasksService } from './tasks.service';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';

@Controller('tasks')
export class TasksController {
  constructor(private readonly tasksService: TasksService) {}

  @Post()
  create(@Body() createTaskDto: CreateTaskDto) {
    return this.tasksService.create(createTaskDto);
  }

  @Get()
  findAll(
    @Query('page') page: number = 1,
    @Query('limit') limit: number = 10,
    @Query('status') status?: string,
    @Query('platform') platform?: string,
  ) {
    return this.tasksService.findAll({
      page: Number(page),
      limit: Number(limit),
      status,
      platform,
    });
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.tasksService.findOne(id);
  }

  @Patch(':id')
  update(@Param('id') id: string, @Body() updateTaskDto: UpdateTaskDto) {
    return this.tasksService.update(id, updateTaskDto);
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return this.tasksService.remove(id);
  }

  @Post(':id/start')
  startTask(@Param('id') id: string) {
    return this.tasksService.startTask(id);
  }

  @Post(':id/retry')
  retryTask(@Param('id') id: string) {
    return this.tasksService.retryTask(id);
  }

  @Get(':id/stats')
  getTaskStats(@Param('id') id: string) {
    return this.tasksService.getTaskStats(id);
  }
}
