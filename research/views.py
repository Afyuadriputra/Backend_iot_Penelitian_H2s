from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from research.serializers import (
    AggregatedTrendPointSerializer,
    ARKLResearchQuerySerializer,
    ARKLResearchResponseSerializer,
    H2SSummarySerializer,
    H2STrendQuerySerializer,
    H2STrendResponseSerializer,
    RawTrendPointSerializer,
    ResearchFilterSerializer,
)
from research.services.arkl_results import (
    ARKLResearchFilters,
    get_arkl_research_results,
)
from research.services.h2s_summary import (
    calculate_h2s_summary,
)
from research.services.h2s_trends import (
    TrendInterval,
    get_h2s_trend,
)

from research.serializers import (
    AlertSummarySerializer,
    ExposureSummarySerializer,
    RiskDistributionQuerySerializer,
    RiskDistributionSerializer,
)
from research.services.alert_summary import (
    calculate_alert_summary,
)
from research.services.exposure_summary import (
    calculate_exposure_summary,
)
from research.services.risk_distribution import (
    calculate_risk_distribution,
)

from django.http import HttpResponse

from research.services.arkl_export import (
    export_arkl_csv,
)


class H2SSummaryView(APIView):
    @extend_schema(
        parameters=[
            ResearchFilterSerializer,
        ],
        responses={
            200: H2SSummarySerializer,
        },
    )
    def get(self, request):
        query_serializer = (
            ResearchFilterSerializer(
                data=request.query_params
            )
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        filters = query_serializer.to_filters()

        summary = calculate_h2s_summary(
            filters=filters
        )

        response_serializer = (
            H2SSummarySerializer(summary)
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class H2STrendView(APIView):
    @extend_schema(
        parameters=[
            H2STrendQuerySerializer,
        ],
        responses={
            200: H2STrendResponseSerializer,
        },
    )
    def get(self, request):
        query_serializer = (
            H2STrendQuerySerializer(
                data=request.query_params
            )
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        filters = query_serializer.to_filters()

        interval = TrendInterval(
            query_serializer.validated_data[
                "interval"
            ]
        )

        series = get_h2s_trend(
            filters=filters,
            interval=interval,
        )

        if interval == TrendInterval.RAW:
            series_data = (
                RawTrendPointSerializer(
                    series,
                    many=True,
                ).data
            )
        else:
            series_data = (
                AggregatedTrendPointSerializer(
                    series,
                    many=True,
                ).data
            )

        response_data = {
            "interval": interval,
            "series": series_data,
        }

        response_serializer = (
            H2STrendResponseSerializer(
                response_data
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )


class ARKLResearchResultView(APIView):
    @extend_schema(
        parameters=[
            ARKLResearchQuerySerializer,
        ],
        responses={
            200: ARKLResearchResponseSerializer,
        },
    )
    def get(self, request):
        query_serializer = (
            ARKLResearchQuerySerializer(
                data=request.query_params
            )
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        data = query_serializer.validated_data

        filters = ARKLResearchFilters(
            calculation_version=(
                data["calculation_version"]
            ),
            worker_code=data.get(
                "worker_code"
            ),
            calculation_type=data.get(
                "calculation_type"
            ),
            source_simulated=data.get(
                "source_simulated"
            ),
            start=data.get("start"),
            end=data.get("end"),
        )

        collection = (
            get_arkl_research_results(
                filters=filters
            )
        )

        response_serializer = (
            ARKLResearchResponseSerializer(
                collection
            )
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

class RiskDistributionView(APIView):
    @extend_schema(
        parameters=[
            RiskDistributionQuerySerializer,
        ],
        responses={
            200: RiskDistributionSerializer,
        },
    )
    def get(self, request):
        query_serializer = (
            RiskDistributionQuerySerializer(
                data=request.query_params
            )
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        data = query_serializer.validated_data

        result = calculate_risk_distribution(
            calculation_version=(
                data["calculation_version"]
            ),
            worker_code=data.get(
                "worker_code"
            ),
            source_simulated=data.get(
                "source_simulated"
            ),
        )

        serializer = (
            RiskDistributionSerializer(
                result
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class ExposureSummaryView(APIView):
    @extend_schema(
        responses={
            200: ExposureSummarySerializer,
        },
    )
    def get(self, request):
        summary = (
            calculate_exposure_summary()
        )

        serializer = (
            ExposureSummarySerializer(
                summary
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class AlertSummaryView(APIView):
    @extend_schema(
        responses={
            200: AlertSummarySerializer,
        },
    )
    def get(self, request):
        summary = (
            calculate_alert_summary()
        )

        serializer = (
            AlertSummarySerializer(
                summary
            )
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

class ARKLExportCSVView(APIView):
    @extend_schema(
        parameters=[
            ARKLResearchQuerySerializer,
        ],
        responses={
            200: {
                "type": "string",
                "format": "binary",
            },
        },
    )
    def get(self, request):
        query_serializer = (
            ARKLResearchQuerySerializer(
                data=request.query_params
            )
        )

        query_serializer.is_valid(
            raise_exception=True
        )

        data = query_serializer.validated_data

        filters = ARKLResearchFilters(
            calculation_version=(
                data["calculation_version"]
            ),
            worker_code=data.get(
                "worker_code"
            ),
            calculation_type=data.get(
                "calculation_type"
            ),
            source_simulated=data.get(
                "source_simulated"
            ),
            start=data.get("start"),
            end=data.get("end"),
        )

        csv_content = export_arkl_csv(
            filters=filters
        )

        response = HttpResponse(
            csv_content,
            content_type=(
                "text/csv; charset=utf-8"
            ),
        )

        version = data[
            "calculation_version"
        ].replace(
            ".",
            "_",
        ).replace(
            "-",
            "_",
        )

        response[
            "Content-Disposition"
        ] = (
            'attachment; '
            f'filename="arkl_results_{version}.csv"'
        )

        return response