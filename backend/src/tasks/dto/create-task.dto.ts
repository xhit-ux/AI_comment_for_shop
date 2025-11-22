import { IsEnum, IsNotEmpty, IsOptional, IsUrl, IsNumber, IsBoolean, IsObject, ValidateNested } from 'class-validator';
import { Type } from 'class-transformer';
import { PlatformType } from '../schemas/task.schema';

class TimeRangeDto {
  @IsOptional()
  @Type(() => Date)
  start?: Date;

  @IsOptional()
  @Type(() => Date)
  end?: Date;
}

export class CreateTaskDto {
  @IsNotEmpty()
  name: string;

  @IsOptional()
  description?: string;

  @IsEnum(PlatformType)
  platform: PlatformType;

  @IsNotEmpty()
  @IsUrl()
  productUrl: string;

  @IsOptional()
  productId?: string;

  @IsNumber()
  maxComments: number;

  @IsBoolean()
  includeFollowUp: boolean;

  @IsBoolean()
  includeImageComments: boolean;

  @IsBoolean()
  includeVideoComments: boolean;

  @IsOptional()
  @IsObject()
  @ValidateNested()
  @Type(() => TimeRangeDto)
  timeRange?: TimeRangeDto;
}
