from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from utils.ocr_processor import SmartDocumentProcessor
from utils.kingdee_integration import KingdeeIntegration
from utils.local_kingdee_integration import LocalKingdeeIntegration, ExcelKingdeeIntegration

class WarehouseAgentSystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ocr_processor = SmartDocumentProcessor(config['OCR_CONFIG'])
        
        # 根据配置选择金蝶集成方式
        kingdee_type = config.get('KINGDEE_TYPE', 'local')
        if kingdee_type == 'online':
            self.kingdee_integration = KingdeeIntegration(config['KINGDEE_ONLINE_CONFIG'])
        elif kingdee_type == 'local':
            self.kingdee_integration = LocalKingdeeIntegration(config['KINGDEE_LOCAL_CONFIG'])
        else:  # excel
            self.kingdee_integration = ExcelKingdeeIntegration(config['KINGDEE_EXCEL_CONFIG'])
        
        # 初始化代理
        self.ocr_agent = self._create_ocr_agent()
        self.validator_agent = self._create_validator_agent()
        self.kingdee_agent = self._create_kingdee_agent()
        self.coordinator_agent = self._create_coordinator_agent()

    def _create_ocr_agent(self) -> Agent:
        """创建OCR识别代理"""
        
        def ocr_tool(image_path: str) -> str:
            """OCR识别工具"""
            result = self.ocr_processor.process_document(image_path)
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        ocr_tool_obj = Tool(
            name="OCR识别工具",
            description="识别纸质单据图片，提取结构化数据",
            func=ocr_tool
        )
        
        return Agent(
            role='OCR识别专家',
            goal='准确识别纸质单据内容，提取结构化数据',
            backstory="""你是一个专业的OCR识别专家，擅长从纸质单据图片中提取准确的文字信息。
            你能够识别各种格式的入库单、出库单，并将其转换为结构化数据。
            你特别注意数字、日期、商品编码等关键信息的准确性。""",
            tools=[ocr_tool_obj],
            verbose=True,
            allow_delegation=False
        )

    def _create_validator_agent(self) -> Agent:
        """创建数据验证代理"""
        
        def validate_data_tool(data_json: str) -> str:
            """数据验证工具"""
            try:
                data = json.loads(data_json)
                validation_result = self._validate_document_data(data)
                return json.dumps(validation_result, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps({'valid': False, 'errors': [f'数据格式错误: {str(e)}']})
        
        validate_tool_obj = Tool(
            name="数据验证工具",
            description="验证单据数据的完整性和准确性",
            func=validate_data_tool
        )
        
        return Agent(
            role='数据验证专家',
            goal='确保单据数据的完整性、准确性和合规性',
            backstory="""你是一个严谨的数据验证专家，负责检查单据数据的质量。
            你会验证必填字段、数据格式、逻辑关系等，确保数据符合业务规则。
            你特别关注数量、金额、日期等关键字段的合理性。""",
            tools=[validate_tool_obj],
            verbose=True,
            allow_delegation=False
        )

    def _create_kingdee_agent(self) -> Agent:
        """创建金蝶集成代理"""
        
        def create_kingdee_document_tool(data_json: str) -> str:
            """金蝶单据创建工具"""
            try:
                data = json.loads(data_json)
                
                if data.get('document_type') == 'inbound':
                    result = self.kingdee_integration.process_inbound_document(data)
                elif data.get('document_type') == 'outbound':
                    result = self.kingdee_integration.process_outbound_document(data)
                else:
                    result = {'success': False, 'error': '未知单据类型'}
                
                return json.dumps(result, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps({'success': False, 'error': f'处理失败: {str(e)}'})
        
        def check_inventory_tool(item_code: str, warehouse_code: str = None) -> str:
            """库存查询工具"""
            result = self.kingdee_integration.check_inventory(item_code, warehouse_code)
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        kingdee_create_tool = Tool(
            name="金蝶单据创建工具",
            description="在金蝶系统中创建入库单或出库单",
            func=create_kingdee_document_tool
        )
        
        inventory_tool = Tool(
            name="库存查询工具",
            description="查询商品在金蝶系统中的库存信息",
            func=check_inventory_tool
        )
        
        return Agent(
            role='金蝶系统集成专家',
            goal='将验证后的单据数据同步到金蝶系统',
            backstory="""你是金蝶系统集成专家，负责将处理好的单据数据同步到金蝶ERP系统。
            你熟悉金蝶的API接口，能够准确创建入库单、出库单，并查询库存信息。
            你会确保数据同步的准确性和完整性。""",
            tools=[kingdee_create_tool, inventory_tool],
            verbose=True,
            allow_delegation=False
        )

    def _create_coordinator_agent(self) -> Agent:
        """创建协调代理"""
        return Agent(
            role='仓管系统协调员',
            goal='协调各个代理完成完整的单据处理流程',
            backstory="""你是仓管系统的协调员，负责统筹整个单据处理流程。
            你会协调OCR识别、数据验证、系统集成等各个环节，确保流程顺畅进行。
            你会根据处理结果提供清晰的反馈和建议。""",
            verbose=True,
            allow_delegation=True
        )

    def process_document(self, image_path: str) -> Dict[str, Any]:
        """处理单据的完整流程"""
        
        # 定义任务
        ocr_task = Task(
            description=f"使用OCR识别工具处理图片: {image_path}，提取单据的结构化数据",
            agent=self.ocr_agent,
            expected_output="包含单据类型、基本信息和商品明细的JSON格式数据"
        )
        
        validation_task = Task(
            description="验证OCR识别结果的数据完整性和准确性，检查必填字段和数据格式",
            agent=self.validator_agent,
            expected_output="数据验证结果，包含验证状态和错误信息（如有）"
        )
        
        kingdee_task = Task(
            description="将验证通过的数据同步到金蝶系统，创建对应的单据",
            agent=self.kingdee_agent,
            expected_output="金蝶系统处理结果，包含单据号和处理状态"
        )
        
        coordination_task = Task(
            description="协调整个处理流程，汇总各环节结果，提供最终处理报告",
            agent=self.coordinator_agent,
            expected_output="完整的处理报告，包含各环节状态和最终结果"
        )
        
        # 创建团队
        crew = Crew(
            agents=[self.ocr_agent, self.validator_agent, self.kingdee_agent, self.coordinator_agent],
            tasks=[ocr_task, validation_task, kingdee_task, coordination_task],
            process=Process.sequential,
            verbose=True
        )
        
        # 执行任务
        try:
            result = crew.kickoff()
            return {
                'success': True,
                'result': result,
                'processed_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }

    def _validate_document_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证单据数据"""
        errors = []
        warnings = []
        
        if not data.get('success'):
            errors.append('OCR识别失败')
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        doc_data = data.get('data', {})
        basic_info = doc_data.get('basic_info', {})
        items = doc_data.get('items', [])
        
        # 验证基本信息
        if not basic_info.get('document_number'):
            errors.append('缺少单据号')
        
        if not basic_info.get('date'):
            warnings.append('缺少日期信息')
        
        doc_type = doc_data.get('document_type')
        if doc_type == 'inbound':
            if not basic_info.get('supplier'):
                errors.append('入库单缺少供应商信息')
        elif doc_type == 'outbound':
            if not basic_info.get('customer'):
                errors.append('出库单缺少客户信息')
        else:
            errors.append('无法识别单据类型')
        
        # 验证商品明细
        if not items:
            errors.append('没有识别到商品明细')
        else:
            for i, item in enumerate(items):
                if not item.get('item_code') and not item.get('item_name'):
                    warnings.append(f'第{i+1}行商品缺少编码或名称')
                
                if not item.get('quantity'):
                    warnings.append(f'第{i+1}行商品缺少数量')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

# 单代理版本（简化版）
class SimpleWarehouseAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ocr_processor = SmartDocumentProcessor(config['OCR_CONFIG'])
        
        # 根据配置选择金蝶集成方式
        kingdee_type = config.get('KINGDEE_TYPE', 'local')
        if kingdee_type == 'online':
            self.kingdee_integration = KingdeeIntegration(config['KINGDEE_ONLINE_CONFIG'])
        elif kingdee_type == 'local':
            self.kingdee_integration = LocalKingdeeIntegration(config['KINGDEE_LOCAL_CONFIG'])
        else:  # excel
            self.kingdee_integration = ExcelKingdeeIntegration(config['KINGDEE_EXCEL_CONFIG'])
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        """简化的单据处理流程"""
        try:
            # 1. OCR识别
            ocr_result = self.ocr_processor.process_document(image_path)
            if not ocr_result['success']:
                return ocr_result
            
            # 2. 数据验证
            doc_data = ocr_result['data']
            validation = self._validate_data(doc_data)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'error': '数据验证失败',
                    'details': validation
                }
            
            # 3. 同步到金蝶
            if doc_data['document_type'] == 'inbound':
                kingdee_result = self.kingdee_integration.process_inbound_document(doc_data)
            elif doc_data['document_type'] == 'outbound':
                kingdee_result = self.kingdee_integration.process_outbound_document(doc_data)
            else:
                return {'success': False, 'error': '未知单据类型'}
            
            return {
                'success': True,
                'ocr_result': ocr_result,
                'validation': validation,
                'kingdee_result': kingdee_result,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'处理失败: {str(e)}',
                'processed_at': datetime.now().isoformat()
            }
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """简化的数据验证"""
        errors = []
        
        basic_info = data.get('basic_info', {})
        items = data.get('items', [])
        
        if not basic_info.get('document_number'):
            errors.append('缺少单据号')
        
        if not items:
            errors.append('没有商品明细')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }