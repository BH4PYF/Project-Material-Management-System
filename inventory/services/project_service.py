from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from django.db.models import Q, Sum
from django.db import transaction

from inventory.models import Project, InboundRecord


class ProjectService:
    """项目管理服务"""
    
    @staticmethod
    def get_projects_with_statistics(search_query: Optional[str] = None, 
                                  status_filter: Optional[str] = None) -> List[Project]:
        """获取项目列表并包含统计信息"""
        projects_qs = Project.objects.all()
        
        # 应用筛选条件
        if search_query:
            projects_qs = projects_qs.filter(
                Q(code__icontains=search_query) | Q(name__icontains=search_query)
            )
        if status_filter is not None and status_filter != '':
            projects_qs = projects_qs.filter(status=status_filter)
        
        # 使用子查询让数据库做 ID 筛选，避免将全部项目对象加载到 Python 内存
        inbound_agg = InboundRecord.objects.filter(
            project_id__in=projects_qs.values('pk')
        ).values('project_id').annotate(
            total_amount_sum=Sum('total_amount')
        )
        
        # 创建聚合映射
        agg_map = {row['project_id']: row['total_amount_sum'] for row in inbound_agg}
        
        # 此处首次求值 projects_qs，加载项目对象并附加统计信息
        projects = list(projects_qs)
        for project in projects:
            project.total_inbound = agg_map.get(project.pk) or 0
        
        return projects
    
    @staticmethod
    def create_project(data: Dict) -> Tuple[Project, Optional[str]]:
        """创建项目"""
        from inventory.views.utils import save_with_generated_code
        
        try:
            with transaction.atomic():
                # 检查名称重复
                existing_by_name = Project.objects.filter(name=data['name']).first()
                if existing_by_name:
                    return None, f'项目名称 "{data["name"]}" 已存在（编号：{existing_by_name.code}），请使用其他名称'
                
                project = Project()
                project.name = data['name']
                project.manager = data.get('manager', '')
                project.location = data.get('location', '')
                project.start_date = data.get('start_date') or None
                project.end_date = data.get('end_date') or None
                project.budget = data.get('budget', Decimal('0'))
                project.status = data.get('status', 'active')
                project.remark = data.get('remark', '')
                
                # 保存对象并生成编号
                if save_with_generated_code(project, 'PRJ', Project):
                    return project, None
                else:
                    return None, '系统繁忙，请稍后重试'
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def update_project(project_id: int, data: Dict) -> Tuple[Project, Optional[str]]:
        """更新项目"""
        try:
            with transaction.atomic():
                project = Project.objects.get(pk=project_id)
                
                # 检查名称重复（排除自身）
                duplicate = Project.objects.filter(name=data['name']).exclude(pk=project_id).first()
                if duplicate:
                    return None, f'项目名称 "{data["name"]}" 已存在（编号：{duplicate.code}），请使用其他名称'
                
                project.name = data['name']
                project.manager = data.get('manager', '')
                project.location = data.get('location', '')
                project.start_date = data.get('start_date') or None
                project.end_date = data.get('end_date') or None
                project.budget = data.get('budget', Decimal('0'))
                project.status = data.get('status', 'active')
                project.remark = data.get('remark', '')
                project.save()
                
                return project, None
        except Project.DoesNotExist:
            return None, '项目不存在'
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def delete_project(project_id: int) -> Tuple[bool, Optional[str]]:
        """删除项目"""
        try:
            project = Project.objects.get(pk=project_id)
            
            # 检查是否有入库记录
            if InboundRecord.all_objects.filter(project=project).exists():
                return False, '该项目已有入库记录，无法删除'
            
            project.delete()
            return True, None
        except Project.DoesNotExist:
            return False, '项目不存在'
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def check_project_name(name: str, exclude_id: Optional[int] = None) -> Tuple[bool, Optional[Dict]]:
        """检查项目名称是否重复"""
        if not name:
            return False, None
        
        query = Project.objects.filter(name=name)
        if exclude_id:
            query = query.exclude(pk=exclude_id)
        
        duplicate = query.first()
        
        if duplicate:
            return True, {
                'code': duplicate.code,
                'message': f'项目名称 "{name}" 已存在'
            }
        
        return False, None
